from typing import TYPE_CHECKING

import base64
import json
import logging
import os
import pickle

from django.conf import settings
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property, classproperty
from django.utils.translation import gettext_lazy as _

import celery
from celery import states
from celery.contrib.abortable import AbortableAsyncResult
from concurrency.api import disable_concurrency
from concurrency.fields import AutoIncVersionField

from hope_country_report.config.celery import app

from ...core.utils import SmartManager
from ..manager import PowerQueryManager
from ..processors import mimetype_map

if TYPE_CHECKING:
    from typing import Any, Dict

    from collections.abc import Callable

logger = logging.getLogger(__name__)

MIMETYPES = [(k, v) for k, v in mimetype_map.items()]


class CeleryEnabled(models.Model):
    # QUEUED (task exists in Redis but unkonw to Celery)
    # CANCELED (task is canceled BEFORE worker fetch it)
    # PENDING (waiting for execution or unknown task id)
    # STARTED (task has been started)
    # SUCCESS (task executed successfully)
    # FAILURE (task execution resulted in exception)
    # RETRY (task is being retried)
    # REVOKED (task has been revoked)
    SCHEDULED = frozenset({states.PENDING, states.RECEIVED, states.STARTED, states.RETRY, "QUEUED"})
    QUEUED = "QUEUED"
    CANCELED = "CANCELED"
    NOT_SCHEDULED = "Not scheduled"

    version = AutoIncVersionField()
    sentry_error_id = models.CharField(max_length=512, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    last_run = models.DateTimeField(null=True, blank=True)

    curr_async_result_id = models.CharField(
        max_length=36, blank=True, null=True, help_text="Current (active) AsyncResult is"
    )
    last_async_result_id = models.CharField(
        max_length=36, blank=True, null=True, help_text="Latest executed AsyncResult is"
    )

    celery_task_name: str = "<define `celery_task_name`>"

    class Meta:
        abstract = True

    def get_celery_queue_position(self) -> int:
        from hope_country_report.config.celery import app

        with app.pool.acquire(block=True) as conn:
            tasks = conn.default_channel.client.lrange(settings.CELERY_TASK_DEFAULT_QUEUE, 0, -1)
        for i, task in enumerate(tasks, 1):
            j = json.loads(task)
            if j["headers"]["id"] == self.curr_async_result_id:
                return i
        return 0

    def celery_queue_status(self) -> "Dict[str, int]":
        with app.pool.acquire(block=True) as conn:
            tasks = conn.default_channel.client.lrange(settings.CELERY_TASK_DEFAULT_QUEUE, 0, 1)
            revoked = list(conn.default_channel.client.smembers(settings.CELERY_TASK_REVOKED_QUEUE))
            pending = len(tasks)
            canceled = 0
            pending_tasks = [json.loads(task)["headers"]["id"].encode() for task in tasks]
            for task_id in pending_tasks:
                if task_id in revoked:
                    pending -= 1
                    canceled += 1

            for rem in revoked:
                if rem not in pending_tasks:
                    conn.default_channel.client.srem(settings.CELERY_TASK_REVOKED_QUEUE, rem)
            return {"size": len(tasks), "pending": pending, "canceled": canceled, "revoked": len(revoked)}

    @cached_property
    def async_result(self) -> "AbortableAsyncResult|None":
        if self.curr_async_result_id:
            return AbortableAsyncResult(self.curr_async_result_id, app=celery.current_app)
        else:
            return None

    @property
    def queue_info(self) -> "Dict[str, Any]":
        with app.pool.acquire(block=True) as conn:
            tasks = conn.default_channel.client.lrange(settings.CELERY_TASK_DEFAULT_QUEUE, 0, -1)

        for task in tasks:
            j = json.loads(task)
            if j["headers"]["id"] == self.async_result.id:
                j["body"] = json.loads(base64.b64decode(j["body"]))
                return j
        return {"id": "NotFound"}

    @property
    def task_info(self) -> "Dict[str, Any]":
        if self.async_result:
            info = self.async_result._get_task_meta()
            result, task_status = info["result"], info["status"]
            if task_status == "STARTED":
                started_at = result.get("start_time", 0)
            else:
                started_at = 0
            last_update = info["date_done"]
            if isinstance(result, Exception):
                error = str(result)
            elif task_status == "REVOKED":
                error = _("Query execution cancelled.")
            else:
                error = ""

            if task_status == "SUCCESS" and not error:
                query_result_id = result
            else:
                query_result_id = None
            return {
                **info,
                # "id": self.async_result.id,
                "last_update": last_update,
                "started_at": started_at,
                "status": task_status,
                "error": error,
                "query_result_id": query_result_id,
            }

    @classproperty
    def task_handler(cls) -> "Callable[Any, Any]":
        from .. import celery_tasks

        return getattr(celery_tasks, cls.celery_task_name)

    def is_queued(self) -> bool:
        from hope_country_report.config.celery import app

        with app.pool.acquire(block=True) as conn:
            tasks = conn.default_channel.client.lrange(settings.CELERY_TASK_DEFAULT_QUEUE, 0, -1)
        for task in tasks:
            j = json.loads(task)
            if j["headers"]["id"] == self.curr_async_result_id:
                return True
        return False

    def is_canceled(self) -> bool:
        with app.pool.acquire(block=True) as conn:
            return conn.default_channel.client.sismember(settings.CELERY_TASK_REVOKED_QUEUE, self.curr_async_result_id)

    @property
    def status(self) -> str:
        try:
            if self.curr_async_result_id:
                if self.is_canceled():
                    return "CANCELED"

                result = self.async_result.state
                if result == "PENDING":
                    if self.is_queued():
                        result = "QUEUED"
                    else:
                        result = "Not scheduled"
            else:
                result = "Not scheduled"
            return result
        except Exception as e:
            return str(e)

    def queue(self) -> str | None:
        if self.status not in self.SCHEDULED:
            ver = self.version
            res = self.task_handler.delay(self.id, self.version)
            with disable_concurrency(self):
                self.curr_async_result_id = res.id
                self.save(update_fields=["curr_async_result_id"])
            assert self.version == ver
            return self.curr_async_result_id
        return None

    def terminate(self) -> None:
        if self.status in ["QUEUED", "PENDING"]:
            with app.pool.acquire(block=True) as conn:
                conn.default_channel.client.sadd(
                    settings.CELERY_TASK_REVOKED_QUEUE, self.curr_async_result_id, self.curr_async_result_id
                )
        else:
            app.control.revoke(self.curr_async_result_id, terminate=True)

    @classmethod
    def discard_all(cls) -> None:
        app.control.discard_all()
        cls.objects.update(curr_async_result_id=None)
        with app.pool.acquire(block=True) as conn:
            conn.default_channel.client.delete(settings.CELERY_TASK_REVOKED_QUEUE)

    @classmethod
    def purge(cls) -> None:
        app.control.purge()


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
            x = self.unmarshall(f)
        return x


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
