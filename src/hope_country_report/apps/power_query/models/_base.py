import datetime
import decimal
import logging
import os
import pickle
import uuid
from typing import TYPE_CHECKING

from concurrency.fields import AutoIncVersionField
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db import models
from django.urls import reverse

from ...core.utils import SmartManager
from ..manager import PowerQueryManager
from ..processors import mimetype_map

if TYPE_CHECKING:
    from typing import Any


logger = logging.getLogger(__name__)

MIMETYPES = [(k, v) for k, v in mimetype_map.items()]


class PowerQueryCeleryFields(models.Model):
    version = AutoIncVersionField()
    sentry_error_id = models.CharField(max_length=512, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    last_run = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class AdminReversable(models.Model):
    class Meta:
        abstract = True

    def get_admin_url(self):
        return reverse(admin_urlname(self._meta, "change"), args=[self.pk])


class PowerQueryModel(AdminReversable, models.Model):
    class Meta:
        abstract = True

    objects = PowerQueryManager()
    _all = SmartManager()


# ``Dataset`` payloads are pickled server-side, but a lower-privileged actor must
# never be able to smuggle a pickle gadget. Only classes produced by the query
# engine are allowed during unpickling; everything else (os/posix/subprocess and
# dangerous builtins such as eval/exec/getattr) is rejected.
_UNPICKLE_ALLOWED_MODULE_PREFIXES = (
    "datetime",
    "decimal",
    "uuid",
    "collections",
    "copyreg",
    "tablib",
    "django.db.models",
    "hope_country_report.apps.hope.models",
)

_UNPICKLE_ALLOWED_BUILTINS = frozenset(
    {
        "NoneType",
        "bool",
        "bytearray",
        "bytes",
        "complex",
        "dict",
        "float",
        "frozenset",
        "int",
        "list",
        "memoryview",
        "object",
        "range",
        "set",
        "slice",
        "str",
        "tuple",
    }
)


# Value types that are safe to reconstruct even when a third party (e.g. test
# tooling) subclasses them.
_UNPICKLE_SAFE_BASES = (
    datetime.date,
    datetime.datetime,
    datetime.time,
    datetime.timedelta,
    decimal.Decimal,
    uuid.UUID,
    models.Model,
)


class SafeUnpickler(pickle.Unpickler):
    """``pickle.Unpickler`` restricted to the classes the query engine emits."""

    def find_class(self, module: str, name: str) -> "Any":
        if module == "builtins":
            if name not in _UNPICKLE_ALLOWED_BUILTINS:
                raise pickle.UnpicklingError(f"Unpickling of builtins.{name} is not allowed")
            return super().find_class(module, name)
        if module.startswith(_UNPICKLE_ALLOWED_MODULE_PREFIXES):
            return super().find_class(module, name)
        cls = super().find_class(module, name)
        if isinstance(cls, type) and issubclass(cls, _UNPICKLE_SAFE_BASES):
            return cls
        raise pickle.UnpicklingError(f"Unpickling of {module}.{name} is not allowed")


class FileProviderMixin(models.Model):
    def get_file_path(self, filename):
        return os.path.join(type(self).__name__.lower(), filename)

    file = models.FileField(null=True, blank=True, upload_to=get_file_path)
    size = models.IntegerField(default=0)

    class Meta:
        abstract = True

    @classmethod
    def marshall(cls, value):
        return pickle.dumps(value)

    @classmethod
    def unmarshall(cls, value):
        return SafeUnpickler(value).load()

    @property
    def data(self) -> "Any":
        if not self.file:
            return None
        with self.file.open("rb") as f:
            return self.unmarshall(f)


class TimeStampMixin(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("updated_on",)


class ManageableObject(models.Model):
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        abstract = True
