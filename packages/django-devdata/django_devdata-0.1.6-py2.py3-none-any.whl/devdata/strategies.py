import json
import pathlib
import subprocess
from tempfile import TemporaryFile
from typing import Set, Tuple

from django.conf import settings
from django.core import serializers
from django.db import models

from .pii_anonymisation import PiiAnonymisingSerializer
from .utils import to_app_model_label, to_model


class Strategy:
    """
    Base strategy defining how to get data for a given model into a fresh
    database.
    """

    def __init__(self):
        pass

    def sync(self, django_dbname, model):
        """Load data into newly created database."""
        raise NotImplementedError


class Exportable:
    """
    A strategy that uses exported data from some source, typically a production
    database.
    """

    seen_names = set()  # type: Set[Tuple[str, str]]

    def __init__(self, *args, name, **kwargs):
        super().__init__(*args, **kwargs)

        self.name = name

    def export(self, django_dbname, model, no_update=False):
        """
        Export the data to a directory on disk. `no_update` indicates not to
        update if there is any data already existing locally.
        """
        pass

    def data_file(self, app_model_label):
        return (
            pathlib.Path(settings.DEVDATA_LOCAL_DIR)
            / app_model_label
            / "{}.json".format(self.name)
        )

    def ensure_dir_exists(self, app_model_label):
        unique_key = (app_model_label, self.name)
        if unique_key in self.seen_names:
            raise ValueError(
                "Exportable strategy names must be unique per model so that "
                "exports do not collide.",
            )
        self.seen_names.add(unique_key)

        model_dir = pathlib.Path(settings.DEVDATA_LOCAL_DIR) / app_model_label
        model_dir.mkdir(exist_ok=True)


class QuerySetStrategy(Exportable, Strategy):
    """Sync a table using an unfiltered QuerySet."""

    use_natural_foreign_keys = False
    use_natural_primary_keys = False

    json_indent = 2

    def __init__(self, *args, restricted_pks=None, anonymise=True, **kwargs):
        super().__init__(*args, **kwargs)

        # Only set in the remote dump process
        self.restricted_pks = restricted_pks
        self.anonymise = anonymise

    def get_kwargs(self, model):
        restricted_pks = {}

        for field in model._meta.fields:
            if not field.related_model:
                continue

            app_model_label = to_app_model_label(field.related_model)
            restricted_pks[app_model_label] = self.get_exported_pks_for_model(
                field.related_model,
            )

        return {
            "name": self.name,
            "anonymise": self.anonymise,
            "restricted_pks": restricted_pks,
        }

    def get_queryset(self, django_dbname, model):
        queryset = model.objects.using(django_dbname)

        for app_model_label, restrict_pks in self.restricted_pks.items():
            restrict_model = to_model(app_model_label)

            # We filter to all fields that relate to the restricted model. This
            # will usually be just one field, but in cases where it's multiple
            # to preserve FK integrity we must restrict all of them.
            fk_fields = [
                x
                for x in model._meta.fields
                if x.related_model == restrict_model
                if x.related_model != model
            ]

            queryset = queryset.filter(
                *[
                    models.Q(
                        **{x.attname: None},
                    )
                    | models.Q(
                        **{"{}__in".format(x.attname): restrict_pks},
                    )
                    for x in fk_fields
                ]
            )

        return queryset

    def export_local(self, django_dbname, model, output):
        queryset = self.get_queryset(django_dbname, model)

        serializer = (
            PiiAnonymisingSerializer()
            if self.anonymise
            else serializers.get_serializer("json")
        )

        serializer.serialize(
            queryset.iterator(),
            indent=self.json_indent,
            use_natural_foreign_keys=self.use_natural_foreign_keys,
            use_natural_primary_keys=self.use_natural_primary_keys,
            stream=output,
        )

    def export(self, django_dbname, model, no_update):
        app_model_label = to_app_model_label(model)
        data_file = self.data_file(app_model_label)

        if no_update and data_file.exists():
            return

        kwargs = self.get_kwargs(model)

        command = settings.DEVDATA_DUMP_COMMAND.split()
        command.append(app_model_label)
        command.append(
            "{}.{}".format(self.__class__.__module__, self.__class__.__name__)
        )
        command.append(django_dbname)

        self.ensure_dir_exists(app_model_label)

        # We pass the kwargs over stdin because if we have large querysets in
        # the upstream dependencies of this there could be too much data to pass
        # in the arguments to exec.
        with TemporaryFile() as temp_f, TemporaryFile("wt") as kwargs_in_f:
            json.dump(kwargs, kwargs_in_f)
            kwargs_in_f.seek(0)

            try:
                subprocess.run(
                    command,
                    stdin=kwargs_in_f,
                    stdout=temp_f,
                    check=True,
                )
            except subprocess.CalledProcessError:
                print(
                    "Failed to export {} ({})".format(
                        app_model_label,
                        self.name,
                    )
                )
                raise

            temp_f.seek(0)

            with data_file.open("wb") as f:
                written = f.write(temp_f.read())

        # Check if we got an empty JSON list, but assume that the file size will
        # be small if so, to prevent reading in huge data files.
        if written < 1000:
            with data_file.open("r") as f:
                if json.load(f) == []:
                    print(
                        "Warning! '{}' exporter for {} selected no data.".format(
                            self.name,
                            app_model_label,
                        )
                    )

    def sync(self, django_dbname, model):
        app_model_label = to_app_model_label(model)

        try:
            with self.data_file(app_model_label).open() as f:
                objects = serializers.deserialize(
                    "json", f, using=django_dbname
                )
                self.sync_objects(django_dbname, model, objects)
        except Exception:
            print("Failed to sync {} ({})".format(app_model_label, self.name))
            raise

    def sync_objects(self, django_dbname, model, objects):
        qs = model.objects.using(django_dbname)
        existing_pks = set(qs.values_list("pk", flat=True))
        qs.bulk_create(
            [x.object for x in objects if x.object.pk not in existing_pks]
        )

    def get_exported_pks_for_model(self, model):
        return [
            str(x["pk"]) for x in self.get_exported_objects_for_model(model)
        ]

    def get_exported_objects_for_model(self, model):
        app_model_label = to_app_model_label(model)
        objects = []

        data_dir = pathlib.Path(settings.DEVDATA_LOCAL_DIR) / app_model_label
        data_files = data_dir.glob("*.json")

        for data_file in data_files:
            with data_file.open() as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print("Invalid file {}".format(data_file))
                    raise

                objects.extend(data)

        return objects


class ExactQuerySetStrategy(QuerySetStrategy):
    """Sync specific rows from a table using a QuerySet filtered to given PKs."""

    def __init__(self, *args, pks, **kwargs):
        super().__init__(*args, **kwargs)
        self.pks = pks

    def get_kwargs(self, model):
        return {**super().get_kwargs(model), "pks": self.pks}

    def get_queryset(self, django_dbname, model):
        return (
            super().get_queryset(django_dbname, model).filter(pk__in=self.pks)
        )


class RandomSampleQuerySetStrategy(QuerySetStrategy):
    """Syncs a random sample from a QuerySet."""

    def __init__(self, *args, count, **kwargs):
        super().__init__(*args, **kwargs)

        self.count = count

    def get_kwargs(self, model):
        return {**super().get_kwargs(model), "count": self.count}

    def get_queryset(self, django_dbname, model):
        return (
            super()
            .get_queryset(django_dbname, model)
            .order_by("?")[: self.count]
        )


class LatestSampleQuerySetStrategy(QuerySetStrategy):
    """Syncs the latest items from a QuerySet."""

    def __init__(self, *args, count, order_by="-id", **kwargs):
        super().__init__(*args, **kwargs)

        self.count = count
        self.order_by = order_by

    def get_kwargs(self, model):
        return {
            **super().get_kwargs(model),
            "count": self.count,
            "order_by": self.order_by,
        }

    def get_queryset(self, django_dbname, model):
        qs = super().get_queryset(django_dbname, model)
        return qs.order_by(self.order_by)[: self.count]


class ModelReverseRelationshipQuerySetStrategy(QuerySetStrategy):
    """
    Base class for inverse relationship queryset exporting.
    Useful for relationships that go the wrong way to work with
    normal dependency analysis. Example:

        class Order(Model):
            user = ForeignKey(User)
            charge = ForeignKey(Charge)

        class Charge(Model):
            ...

    Requires a dependent model, such as `User`, and defines an additional
    explicit dependency on that model locally. Reads in those IDs, passes them
    to the exporting process, where they are available to `get_queryset`.
    """

    depends_on = NotImplemented  # type: Tuple[str, ...]

    def __init__(self, *args, reverse_filter=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.reverse_filter = reverse_filter

    def get_kwargs(self, model):
        return {
            **super().get_kwargs(model),
            "reverse_filter": self.get_reverse_filter(model),
        }

    def get_reverse_filter(self, model):
        raise NotImplementedError

    def get_queryset(self, django_dbname, model):
        qs = super().get_queryset(django_dbname, model)
        return qs.filter(**self.reverse_filter)


class FactoryStrategy(Strategy):
    """
    Use the provided factory/factories to create data for this model (and any
    related) models.
    """

    def __init__(self, *args, factories, **kwargs):
        super().__init__(*args, **kwargs)
        self.factories = factories

    def sync(self, django_dbname, model):
        pass
