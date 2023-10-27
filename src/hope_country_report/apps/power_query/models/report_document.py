from typing import TYPE_CHECKING

import logging

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import models
from django.utils.functional import cached_property

from django_cleanup import cleanup
from sentry_sdk import capture_exception

from hope_country_report.state import state
from hope_country_report.utils.perf import profile

from ..json import PQJSONEncoder
from ..manager import PowerQueryManager
from ..processors import mimetype_map
from ._base import FileProviderMixin, PowerQueryModel, TimeStampMixin
from .dataset import Dataset
from .formatter import Formatter
from .report import Report

if TYPE_CHECKING:
    from typing import Tuple

    from ...core.models import CountryOffice


logger = logging.getLogger(__name__)

MIMETYPES = [(k, v) for k, v in mimetype_map.items()]


class ReportDocumentManager(PowerQueryManager["ReportDocument"]):
    def get_queryset(self) -> "models.QuerySet[ReportDocument]":
        return super().get_queryset()


@cleanup.select
class ReportDocument(PowerQueryModel, FileProviderMixin, TimeStampMixin, models.Model):
    title = models.CharField(max_length=300)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="documents")
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, blank=True, null=True)
    formatter = models.ForeignKey(Formatter, on_delete=models.SET_NULL, blank=True, null=True)

    arguments = models.JSONField(default=dict, encoder=PQJSONEncoder)
    limit_access_to = models.ManyToManyField(get_user_model(), blank=True, related_name="+")
    info = models.JSONField(default=dict, blank=True, null=False)
    objects = ReportDocumentManager()

    class Meta:
        unique_together = ("report", "dataset", "formatter")

    class Tenant:
        tenant_filter_field = "report__query__country_office"

    def __str__(self) -> str:
        return self.title

    @classmethod
    def process(self, report: "Report", dataset: "Dataset", formatter: "Formatter") -> "Tuple[int|None, Exception|str]":
        try:
            context = dataset.arguments or {}
            try:
                title = report.title.format(**context)
            except KeyError:
                title = report.title
            key = {"report": report, "dataset": dataset, "formatter": formatter}
            try:
                with state.set(tenant=report.country_office):
                    with profile() as perfs:
                        output = formatter.render(
                            {
                                "dataset": dataset,
                                "report": report,
                                "title": title,
                                "context": context,
                            }
                        )
                content = ContentFile(
                    output, name=f"r{report.pk}_ds{dataset.pk}_fmt{formatter.pk}{formatter.file_suffix}"
                )
                if doc := ReportDocument.objects.filter(**key).first():
                    if doc.file:
                        doc.file.delete()
                    doc.file = content
                    doc.save()
                else:
                    doc = ReportDocument.objects.create(
                        **key, file=content, title=title, arguments=dataset.arguments, info=perfs
                    )
                result = doc.pk, doc.file.name
            except Exception as exc:
                sid = capture_exception(exc)
                if doc := ReportDocument.objects.filter(**key).first():
                    doc.delete()
                result = sid, type(exc)
        except Exception as exc:
            logger.exception(exc)
            raise
        return result

    @cached_property
    def country_office(self) -> "CountryOffice":
        return self.report.country_office

    @cached_property
    def file_suffix(self) -> str:
        return self.formatter.processor.file_suffix

    @cached_property
    def content_type(self) -> str:
        return self.formatter.content_type

    # @cached_property
    # def size(self) -> int:
    #     return len(self.output)

    # def get_absolute_url(self) -> str:
    #     return reverse("power_query:document", args=[self.report.pk, self.pk])
