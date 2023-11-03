from typing import TYPE_CHECKING

import itertools
import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from natural_keys import NaturalKeyModel

from ...core.models import CountryOffice
from ..processors import mimetype_map
from ._base import AdminReversable

if TYPE_CHECKING:
    from typing import Any, Dict, List

    from collections.abc import Iterable

logger = logging.getLogger(__name__)

MIMETYPES = [(k, v) for k, v in mimetype_map.items()]


def validate_queryargs(value: "Any") -> None:
    try:
        if not isinstance(value, dict):
            raise ValidationError("QueryArgs must be a dict")
        product = list(itertools.product(*value.values()))
        [dict(zip(value.keys(), e)) for e in product]
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(
            "%(exc)s: " "%(value)s is not a valid QueryArgs",
            params={"value": value, "exc": e},
        )


class Parametrizer(NaturalKeyModel, AdminReversable, models.Model):
    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE, blank=True, null=True)
    code = models.SlugField(max_length=255, unique=True, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255, null=True, blank=True)
    value = models.JSONField(default=dict, blank=False, validators=[validate_queryargs])
    system = models.BooleanField(blank=True, default=False, editable=False)
    source = models.ForeignKey("Query", blank=True, null=True, on_delete=models.CASCADE, related_name="+")

    class Meta:
        verbose_name_plural = "Arguments"
        verbose_name = "Arguments"

    class Tenant:
        tenant_filter_field = "country_office"

    def clean(self) -> None:
        validate_queryargs(self.value)

    def get_matrix(self) -> "List[Dict[str,str]]":
        if isinstance(self.value, dict):
            product = list(itertools.product(*self.value.values()))
            return [dict(zip(self.value.keys(), e)) for e in product]
        else:
            param = slugify(self.code).replace("-", "_")
            return [{param: e} for e in self.value]

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: "Iterable[str] | None" = None,
    ) -> None:
        if not self.code:
            self.code = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

    def refresh(self) -> None:
        if self.source:
            out, __ = self.source.run(use_existing=True)
            self.value = list(out.data)
            self.save()

    def __str__(self) -> str:
        return self.name
