import logging
from collections.abc import Iterable
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import models
from django.utils.text import slugify

from hope_country_report.apps.core.models import CountryOffice
from hope_country_report.apps.power_query.utils import is_valid_template

logger = logging.getLogger(__name__)


class ReportTemplate(models.Model):
    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    doc = models.FileField()
    file_suffix = models.CharField(max_length=20)

    class Tenant:
        tenant_filter_field = "country_office"

    @classmethod
    def load(cls) -> None:
        template_dir = Path(settings.PACKAGE_DIR) / "apps" / "power_query" / "doc_templates"
        for filename in template_dir.glob("*.*"):
            if is_valid_template(filename):
                record_name = f"{slugify(filename.stem)}{filename.suffix}"
                ReportTemplate.objects.get_or_create(
                    name=record_name,
                    defaults={
                        "doc": File(filename.open("rb"), record_name),
                        "file_suffix": filename.suffix,
                    },
                )

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: "Iterable[str] | None" = None,
    ) -> None:
        self.file_suffix = Path(self.doc.name).suffix
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return str(self.name)