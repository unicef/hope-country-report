from typing import TYPE_CHECKING

import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from django_celery_beat.models import PeriodicTask
from taggit.managers import TaggableManager

from ....utils.mail import notify_report_completion
from ...core.models import CountryOffice
from ..json import PQJSONEncoder
from ..processors import mimetype_map
from ._base import AdminReversable, CeleryEnabled, ManageableObject, PowerQueryModel, TimeStampMixin
from .formatter import Formatter
from .query import Query

if TYPE_CHECKING:
    from typing import Any, Optional

    from ....types.pq import ReportResult
    from .dataset import Dataset

logger = logging.getLogger(__name__)

MIMETYPES = [(k, v) for k, v in mimetype_map.items()]


class ReportConfiguration(
    PowerQueryModel, ManageableObject, CeleryEnabled, AdminReversable, TimeStampMixin, models.Model
):
    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE, blank=True, null=True)

    title = models.CharField(max_length=255, blank=False, null=False, verbose_name="Report Title")
    name = models.CharField(max_length=255, blank=True, null=True)
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    description = models.TextField(max_length=255, null=True, blank=True, default="")

    formatters = models.ManyToManyField(Formatter, blank=False)
    active = models.BooleanField(default=True)
    visible = models.BooleanField(default=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="+")
    limit_access_to = models.ManyToManyField(
        get_user_model(), blank=True, related_name="+", help_text=_("Limit access to selected users")
    )
    schedule = models.ForeignKey(
        PeriodicTask,
        verbose_name=_("Scheduling"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="reports",
    )
    notify_to = models.ManyToManyField(
        get_user_model(),
        blank=True,
        related_name="+",
        help_text=_("Users to be notified when report have been created/updated"),
    )

    last_run = models.DateTimeField(null=True, blank=True)

    context = models.JSONField(
        default=dict, encoder=PQJSONEncoder, blank=True, help_text=_("Extra to add to the report context")
    )

    compress = models.BooleanField(default=False, blank=True, help_text=_("Compress reports with Zip"))
    protect = models.BooleanField(
        default=False, blank=True, help_text=_("Protect zip file with system generated password")
    )
    pwd = models.CharField(
        editable=False, blank=True, null=True, help_text=_("Auto generated password to protect .zip files")
    )

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
        self.update_or_create_children()

    def update_or_create_children(self):
        if self.query.abstract:
            defaults = {
                field: getattr(self, field)
                for field in [
                    "active",
                    "compress",
                    "description",
                    "context",
                    "owner",
                    "schedule",
                    "title",
                    "protect",
                    "pwd",
                    "visible",
                ]
            }

            for q in self.query.children:
                rc, _ = ReportConfiguration.objects.get_or_create(
                    parent=self, query=q, country_office=q.country_office, defaults=defaults
                )
                rc.formatters.set(self.formatters.all())
                rc.tags.set(self.tags.all())

    def clean(self) -> None:
        if self.protect and not self.owner:
            raise ValidationError("Cannot protect document without owner")

    def execute(self, run_query: bool = False, notify: bool = True) -> "ReportResult":
        import secrets
        import string

        from .report_document import ReportDocument

        alphabet = string.ascii_letters + string.digits + string.punctuation
        query: Query = self.query
        dataset: "Dataset"
        result: "ReportResult" = []
        if run_query:
            query_result = query.execute_matrix()
            if "error_message" in query_result:
                return [(BaseException("Query Error"), query_result["error_message"])]
        if not self.formatters.exists():
            result = [(None, _("No Formatters available"))]
        elif not query.datasets.exists():
            result = [(None, _("No Dataset available"))]
        else:
            if self.protect:
                self.pwd = "".join(secrets.choice(alphabet) for i in range(12))
                self.save()
            for dataset in query.datasets.all():
                for formatter in self.formatters.all():
                    res = ReportDocument.process(self, dataset, formatter, notify=notify)
                    result.append(res)
            self.refresh_from_db()
            self.last_run = timezone.now()
            self.save()
        if notify and self.documents.exists():
            notify_report_completion(self)
        return result

    def __str__(self) -> str:
        return self.name or ""

    def artifacts(self) -> str:
        return self.documents.distinct("dataset")

    def get_absolute_url(self):
        return reverse("office-config", args=[self.country_office.slug, self.pk])

    def get_documents_url(self):
        base = reverse("office-doc-list", args=[self.country_office.slug])
        return f"{base}?report={self.name}"
