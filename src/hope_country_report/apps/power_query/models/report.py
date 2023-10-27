from typing import TYPE_CHECKING

import logging

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from django_celery_beat.models import PeriodicTask
from taggit.managers import TaggableManager

from ...core.models import CountryOffice
from ..processors import mimetype_map
from ._base import AdminReversable, CeleryEnabled, TimeStampMixin
from .formatter import Formatter
from .query import Query

if TYPE_CHECKING:
    from typing import Any, Optional

    from ....types.pq import ReportResult
    from .dataset import Dataset

logger = logging.getLogger(__name__)

MIMETYPES = [(k, v) for k, v in mimetype_map.items()]


class Report(CeleryEnabled, AdminReversable, TimeStampMixin, models.Model):
    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE, blank=True, null=True)

    title = models.CharField(max_length=255, blank=False, null=False, verbose_name="Report Title")
    name = models.CharField(max_length=255, blank=True, null=True)
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    description = models.TextField(max_length=255, null=True, blank=True, default="")

    formatters = models.ManyToManyField(Formatter, blank=False)
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(get_user_model(), blank=True, null=True, on_delete=models.CASCADE, related_name="+")
    limit_access_to = models.ManyToManyField(get_user_model(), blank=True, related_name="+")
    schedule = models.ForeignKey(PeriodicTask, blank=True, null=True, on_delete=models.SET_NULL, related_name="reports")
    last_run = models.DateTimeField(null=True, blank=True)
    validity_days = models.IntegerField(default=365)

    tags = TaggableManager(blank=True)
    celery_task_name = "refresh_report"

    class Tenant:
        tenant_filter_field = "country_office"

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: "Optional[Any]" = None,
        update_fields: "Optional[Any]" = None,
    ) -> None:
        if not self.name:
            self.name = slugify(self.title)
        super().save(force_insert, force_update, using, update_fields)

    def execute(self, run_query: bool = False) -> "ReportResult":
        from .report_document import ReportDocument

        query: Query = self.query
        dataset: "Dataset"
        result: "ReportResult" = []
        if run_query:
            query.execute_matrix()
        for dataset in query.datasets.all():
            for formatter in self.formatters.all():
                res = ReportDocument.process(self, dataset, formatter)
                result.append(res)
        self.last_run = timezone.now()
        self.save()
        if not result:
            result = ["No Dataset available"]
        return result

    def __str__(self) -> str:
        return self.name or ""

    # def get_absolute_url(self) -> str:
    #     return reverse("power_query:report", args=[self.pk])
