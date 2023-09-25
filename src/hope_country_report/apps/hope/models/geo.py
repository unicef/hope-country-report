from typing import Any, Dict, List

from django.contrib.gis.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _

from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel
from mptt.querysets import TreeQuerySet

from ._base import HopeModel


class ValidityQuerySet(TreeQuerySet):
    def active(self, *args: Any, **kwargs: Any) -> Any:
        return super().filter(valid_until__isnull=True).filter(*args, **kwargs)


class ValidityManager(TreeManager):
    _queryset_class = ValidityQuerySet


class Country(MPTTModel, HopeModel):
    name = models.CharField(max_length=255, db_index=True)
    short_name = models.CharField(max_length=255, db_index=True)
    iso_code2 = models.CharField(max_length=2, unique=True)
    iso_code3 = models.CharField(max_length=3, unique=True)
    iso_num = models.CharField(max_length=4, unique=True)
    parent = TreeForeignKey("self", related_name="children", db_index=True, on_delete=models.CASCADE)
    valid_from = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    extras = JSONField(default=dict, blank=True)

    objects = ValidityManager()

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ("name",)
        db_table = "geo_country"

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_choices(cls) -> List[Dict[str, Any]]:
        queryset = cls.objects.all().order_by("name")
        return [
            {
                "label": {"English(EN)": country.name},
                "value": country.iso_code3,
            }
            for country in queryset
        ]


class AreaType(MPTTModel, HopeModel):
    name = models.CharField(max_length=255, db_index=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    area_level = models.PositiveIntegerField(default=1)
    parent = TreeForeignKey("self", db_index=True, null=True, on_delete=models.CASCADE)
    valid_from = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    extras = JSONField(default=dict, blank=True)

    objects = ValidityManager()

    class Meta:
        verbose_name_plural = "Area Types"
        db_table = "geo_areatype"

    def __str__(self) -> str:
        return self.name


class Area(MPTTModel, HopeModel):
    name = models.CharField(max_length=255)
    parent = TreeForeignKey("self", db_index=True, on_delete=models.CASCADE, verbose_name=_("Parent"))
    p_code = models.CharField(max_length=32, blank=True, null=True, verbose_name="P Code")
    area_type = models.ForeignKey(AreaType, on_delete=models.CASCADE)

    geom = models.MultiPolygonField(null=True, blank=True)
    point = models.PointField(null=True, blank=True)

    valid_from = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    extras = JSONField(default=dict, blank=True)

    class Meta:
        db_table = "geo_area"
