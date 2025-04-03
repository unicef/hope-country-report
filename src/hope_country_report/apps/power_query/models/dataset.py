import logging

from django.db import models
from django.db.models import JSONField
from django.utils.functional import cached_property

from django_cleanup import cleanup

from ...core.models import CountryOffice
from ._base import FileProviderMixin, PowerQueryModel, TimeStampMixin
from .query import Query


logger = logging.getLogger(__name__)


@cleanup.select
class Dataset(PowerQueryModel, FileProviderMixin, TimeStampMixin, models.Model):
    hash = models.CharField(unique=True, max_length=200, editable=False)
    last_run = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=100)
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name="datasets")

    info = JSONField(default=dict, blank=True)

    class Tenant:
        tenant_filter_field = "query__country_office"

    def __str__(self) -> str:
        return f"Result of {self.query.name} {self.arguments}"

    @cached_property
    def country_office(self) -> "CountryOffice":
        return self.query.country_office

    @cached_property
    def arguments(self) -> "dict[str, int|str]":
        return self.info.get("arguments", {}) or {}

    @cached_property
    def extra(self) -> "dict[str, int|str]":
        return self.info.get("extra", {}) or {}
