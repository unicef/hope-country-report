from itertools import islice
from typing import TYPE_CHECKING

import logging

from django.core.exceptions import ValidationError
from django.db import models

from strategy_field.fields import StrategyField
from strategy_field.utils import fqn

from ...core.models import CountryOffice
from ..processors import mimetype_map, ProcessorStrategy, registry, ToHTML, TYPE_LIST, TYPES, TYPE_DETAIL
from ._base import MIMETYPES
from .report_template import ReportTemplate

if TYPE_CHECKING:
    from typing import Any, Dict

    from collections.abc import Iterable

logger = logging.getLogger(__name__)


def batched(iterable, n):
    """Batch data into lists of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be >= 1")
    it = iter(iterable)
    while batch := list(islice(it, n)):
        yield batch


class Formatter(models.Model):
    processor: "ProcessorStrategy"

    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE, blank=True, null=True)

    name = models.CharField(max_length=255, unique=True)
    code = models.TextField(blank=True, null=True)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, blank=True, null=True)

    file_suffix = models.CharField(max_length=10, choices=MIMETYPES)
    processor = StrategyField(registry=registry, default=fqn(ToHTML))
    type = models.IntegerField(choices=TYPES, default=TYPE_LIST)

    compress = models.BooleanField(default=False, blank=True)
    item_per_page = models.SmallIntegerField(default=0)

    class Tenant:
        tenant_filter_field = "country_office"

    def __str__(self) -> str:
        return self.name

    @property
    def content_type(self):
        return mimetype_map[self.file_suffix]

    def clean(self) -> None:
        if self.code and self.template:
            raise ValidationError("You cannot set both 'template' and 'code'")
        self.processor.validate()

    def render(self, context: "Dict[str, Any]") -> bytearray:
        ret = bytearray()
        if self.type == TYPE_LIST:
            ret.extend(self.processor.process(context))
        elif self.type == TYPE_DETAIL:
            ds = context.pop("dataset")
            if self.item_per_page > 1:
                datasets = []
                for dataset in batched(ds.data, self.item_per_page):
                    datasets.append(dataset)
                context["records"] = datasets
                ret.extend(self.processor.process(context))
            else:
                for page, entry in enumerate(ds.data, 1):
                    context["page"] = page
                    context["record"] = entry
                    ret.extend(self.processor.process(context))
        else:
            raise ValueError("Invalid type")
        return ret

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: "str|None" = None,
        update_fields: "Iterable[str]|None" = None,
    ) -> None:
        if not self.file_suffix:
            self.file_suffix = self.processor.file_suffix
        super().save(force_insert, force_update, using, update_fields)
