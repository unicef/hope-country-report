from typing import TYPE_CHECKING

import logging
import tempfile
from functools import partial
from io import BytesIO
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.urls import reverse
from django.utils.functional import cached_property

import pyminizip
from django_cleanup import cleanup
from sentry_sdk import capture_exception

from ....state import state
from ....utils.mail import send_document_password
from ....utils.os import pushd
from ....utils.perf import profile
from ...core.models import CountryOffice
from ..json import PQJSONEncoder
from ..processors import mimetype_map
from ._base import FileProviderMixin, PowerQueryModel, TimeStampMixin
from .dataset import Dataset
from .formatter import Formatter
from .report import ReportConfiguration

if TYPE_CHECKING:
    from typing import Tuple


logger = logging.getLogger(__name__)

MIMETYPES = [(k, v) for k, v in mimetype_map.items()]


@cleanup.select
class ReportDocument(PowerQueryModel, FileProviderMixin, TimeStampMixin, models.Model):
    title = models.CharField(max_length=300)
    report = models.ForeignKey(ReportConfiguration, on_delete=models.CASCADE, related_name="documents")
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, blank=True, null=True)
    formatter = models.ForeignKey(Formatter, on_delete=models.SET_NULL, blank=True, null=True)

    arguments = models.JSONField(default=dict, encoder=PQJSONEncoder)
    limit_access_to = models.ManyToManyField(get_user_model(), blank=True, related_name="+")
    info = models.JSONField(default=dict, blank=True, null=False)

    class Meta:
        unique_together = ("report", "dataset", "formatter")
        permissions = (("download_reportdocument", "Can download Document"),)

    class Tenant:
        tenant_filter_field = "report__country_office"

    def __str__(self) -> str:
        return self.title

    def formats(self):
        return ReportDocument.objects.filter(report=self.report, dataset=self.dataset)

    @classmethod
    def process(
        self, report: "ReportConfiguration", dataset: "Dataset", formatter: "Formatter"
    ) -> "Tuple[int|None, Exception|str]":
        try:
            context = {
                **dataset.arguments,
                **dataset.extra,
                **report.context,
            }
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
                # content = ContentFile(
                #     output, name=f"r{report.pk}_ds{dataset.pk}_fmt{formatter.pk}{formatter.file_suffix}"
                # )
                filename = f"r{report.pk}_ds{dataset.pk}_fmt{formatter.pk}{formatter.file_suffix}"
                notify = False
                values = {
                    "title": title,
                    "info": perfs,
                    "arguments": dataset.arguments,
                }
                if report.compress:
                    from zipfile import ZIP_DEFLATED, ZipFile

                    if report.protect:
                        notify = True
                        with tempfile.TemporaryDirectory(prefix="___") as tdir:
                            with pushd(tdir):
                                sourceFile = Path(filename)
                                sourceFile.write_bytes(output)

                                destinationFile = Path(f"{sourceFile}.zip")
                                password = report.pwd
                                compression_level = 0
                                pyminizip.compress(
                                    str(sourceFile.absolute()),
                                    None,
                                    str(destinationFile.absolute()),
                                    password,
                                    compression_level,
                                )
                                content = ContentFile(Path(destinationFile).read_bytes(), destinationFile.name)

                    else:
                        mf = BytesIO()
                        with ZipFile(mf, mode="w", compression=ZIP_DEFLATED) as zf:
                            zf.writestr(filename, output)
                        content = ContentFile(mf.getvalue(), name=f"{filename}.zip")
                else:
                    content = ContentFile(output, name=filename)

                if doc := ReportDocument.objects.filter(**key).first():
                    if doc.file:
                        doc.file.delete()
                    doc.file = content
                    for k, v in values.items():
                        setattr(doc, k, v)
                    doc.save()
                else:
                    doc = ReportDocument.objects.create(**key, file=content, **values)
                result = doc.pk, doc.file.name

                if notify:
                    send_mail_on_commit = partial(send_document_password, report.owner, doc)
                    transaction.on_commit(send_mail_on_commit)

            except Exception as exc:
                sid = capture_exception(exc)
                logger.exception(exc)
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
    def compressed(self) -> bool:
        return self.report.compress

    @cached_property
    def protected(self) -> bool:
        return self.report.protect

    @cached_property
    def file_suffix(self) -> str:
        return Path(self.file.name).suffix

    @cached_property
    def content_type(self) -> str:
        return mimetype_map[self.file_suffix]

    def get_absolute_url(self):
        return reverse("office-doc", args=[self.country_office.slug, self.pk])
