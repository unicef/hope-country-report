from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models import JSONField

from ...core.models import CountryOffice
from ._base import FileProviderMixin, PowerQueryModel
from .query import Query

if TYPE_CHECKING:
    from typing import Dict

logger = logging.getLogger(__name__)


class Dataset(PowerQueryModel, FileProviderMixin, models.Model):
    hash = models.CharField(unique=True, max_length=200, editable=False)
    last_run = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=100)
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name="datasets")

    info = JSONField(default=dict, blank=True)
    extra = models.BinaryField(null=True, blank=True, help_text="Any other attribute to pass to the formatter")

    class Tenant:
        tenant_filter_field = "query__country_office"

    def __str__(self) -> str:
        return f"Result of {self.query.name} {self.arguments}"

    @property
    def country_office(self) -> "CountryOffice":
        return self.query.country_office

    @property
    def arguments(self) -> "Dict[str, int|str]":
        return self.info.get("arguments", {})
