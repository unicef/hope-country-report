import itertools
import logging
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from natural_keys import NaturalKeyModel

from ...core.models import CountryOffice
from ..processors import mimetype_map
from ._base import AdminReversable

if TYPE_CHECKING:
    from typing import Any, Iterable

logger = logging.getLogger(__name__)

MIMETYPES = [(k, v) for k, v in mimetype_map.items()]


def get_matrix(param, input_: "Iterable" = None) -> "list[dict[str,str]]":
    if isinstance(input_, dict):
        product = list(itertools.product(*input_.values()))
        return [dict(zip(input_.keys(), e, strict=False)) for e in product]
    param = slugify(param).replace("-", "_")
    return [{param: e} for e in input_]


def validate_queryargs(value: "Any") -> bool:
    try:
        get_matrix("test", value)
        return True
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(
            "%(exc)s: %(value)s is not a valid QueryArgs",
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
        ordering = ["name"]

    class Tenant:
        tenant_filter_field = "country_office"

    def clean(self) -> None:
        return validate_queryargs(self.value)

    def get_matrix(self, value: "dict|list|tuple|None" = None) -> "list[dict[str,str]]":
        input = value or self.value
        param = slugify(self.code).replace("-", "_")
        return get_matrix(param, input)

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
