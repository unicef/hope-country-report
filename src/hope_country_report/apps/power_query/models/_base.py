from typing import TYPE_CHECKING

import logging
import os
import pickle

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db import models
from django.urls import reverse

from concurrency.fields import AutoIncVersionField

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
        return pickle.load(value)

    @property
    def data(self) -> "Any":
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
