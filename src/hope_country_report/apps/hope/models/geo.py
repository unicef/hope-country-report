from django.contrib.gis.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _

from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from ._base import HopeModel


class Country(MPTTModel, HopeModel):
    id = models.CharField(primary_key=True, max_length=100, editable=False)
    name = models.CharField(max_length=255, db_index=True)
    short_name = models.CharField(max_length=255, db_index=True)
    iso_code2 = models.CharField(max_length=2, unique=True)
    iso_code3 = models.CharField(max_length=3, unique=True)
    iso_num = models.CharField(max_length=4, unique=True)
    parent = TreeForeignKey("self", blank=True, null=True, db_index=True, on_delete=models.CASCADE)
    valid_from = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    extras = JSONField(default=dict, blank=True)

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ("name",)
        db_table = "geo_country"

    class Tenant:
        tenant_filter_field = "__all__"

    def __str__(self) -> str:
        return self.name


class AreaType(MPTTModel, HopeModel):
    id = models.CharField(primary_key=True, max_length=100, editable=False)
    name = models.CharField(max_length=255, db_index=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    area_level = models.PositiveIntegerField(default=1)
    parent = TreeForeignKey("self", db_index=True, null=True, on_delete=models.CASCADE)
    valid_from = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    extras = JSONField(default=dict, blank=True)

    class Meta:
        verbose_name_plural = "Area Types"
        db_table = "geo_areatype"
        unique_together = ("country", "area_level", "name")

    class Tenant:
        tenant_filter_field = "__all__"

    def __str__(self) -> str:
        return self.name


class Area(MPTTModel, HopeModel):
    id = models.CharField(primary_key=True, max_length=100, editable=False)
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
        unique_together = ("name", "p_code")
        ordering = ("name",)

    class Tenant:
        tenant_filter_field = "__all__"

    def __str__(self):
        return str(self.name)
