import logging
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

import pyzipper
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.functional import cached_property
from pathvalidate import sanitize_filename
from sentry_sdk import capture_exception

from ....state import state
from ....utils.os import pushd
from ....utils.perf import profile
from ..json import PQJSONEncoder
from ..processors import mimetype_map
from ._base import FileProviderMixin, PowerQueryModel, TimeStampMixin
from .dataset import Dataset
from .formatter import Formatter
from .report import ReportConfiguration

if TYPE_CHECKING:
    from typing import Tuple

    from ...core.models import CountryOffice


logger = logging.getLogger(__name__)

MIMETYPES = [(k, v) for k, v in mimetype_map.items()]


# @cleanup.select
class ReportDocument(PowerQueryModel, FileProviderMixin, TimeStampMixin, models.Model):
    title = models.CharField(max_length=300)
    report = models.ForeignKey(ReportConfiguration, on_delete=models.CASCADE, related_name="documents")
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, blank=True, null=True)
    formatter = models.ForeignKey(Formatter, on_delete=models.SET_NULL, blank=True, null=True)

    arguments = models.JSONField(default=dict, encoder=PQJSONEncoder)
    # limit_access_to = models.ManyToManyField(get_user_model(), blank=True, related_name="+")
    info = models.JSONField(default=dict, blank=True, null=False)

    class Meta:
        unique_together = ("report", "dataset", "formatter")
        permissions = (("download_reportdocument", "Can download Document"),)

    class Tenant:
        tenant_filter_field = "report__country_office"

    def __str__(self) -> str:
        return f"{self.title}-{self.formatter.file_suffix}"

    def formats(self):
        return ReportDocument.objects.filter(report=self.report, dataset=self.dataset)

    @cached_property
    def filename(self):
        args_desc = "_".join([str(value) for value in self.arguments.values()])
        return sanitize_filename(f"{self.title}_{args_desc}{self.file_suffix}").lower()

    @classmethod
    def process(
        cls, report: "ReportConfiguration", dataset: "Dataset", formatter: "Formatter", notify: bool = True
    ) -> "Tuple[int|None, Exception|str]":  # noqa
        try:
            args_desc = "_".join([str(value) for value in dataset.arguments.values()])
            context = {
                **dataset.arguments,
                **dataset.extra,
                **report.context,
            }
            try:
                title = f"{report.title.format(**context)}{args_desc}".title()
            except KeyError:
                title = report.title
            key = {"report": report, "dataset": dataset, "formatter": formatter}
            try:
                with timezone.override(report.country_office.timezone):
                    with translation.override(report.country_office.locale):
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
                filename = f"r{report.pk}_ds{dataset.pk}_fmt{formatter.pk}{formatter.file_suffix}"
                values = {
                    "title": title,
                    "info": {"perf": perfs},
                    "arguments": dataset.arguments,
                }
                if report.compress:
                    values["info"]["zip"] = {
                        "content_type": formatter.content_type,
                        "file_suffix": formatter.file_suffix,
                    }
                    if report.protect:
                        with TemporaryDirectory(prefix="___") as tdir, pushd(tdir):
                            source_file = Path(filename)
                            source_file.write_bytes(output)

                            destination_file = Path(f"{source_file}.zip")
                            password = report.pwd

                            with pyzipper.AESZipFile(
                                destination_file,
                                "w",
                                compression=pyzipper.ZIP_DEFLATED,
                                encryption=pyzipper.WZ_AES,
                            ) as zf:
                                zf.setpassword(password.encode("utf-8"))
                                zf.writestr(filename, output)

                            content = ContentFile(destination_file.read_bytes(), destination_file.name)
                    else:
                        mf = BytesIO()
                        with pyzipper.AESZipFile(mf, mode="w", compression=pyzipper.ZIP_DEFLATED) as zf:
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

    def get_absolute_url(self) -> str:
        return reverse("office-doc", args=[self.country_office.slug, self.pk])
