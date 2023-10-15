from typing import TYPE_CHECKING

from django.db import models
from django.db.models import QuerySet
from django.utils.functional import cached_property

from hope_country_report.apps.hope.models._base import HopeModel
from hope_country_report.apps.tenant.db import TenantManager
from hope_country_report.apps.tenant.utils import get_selected_tenant, must_tenant

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice


class BusinessAreaManager(TenantManager["BusinessArea"]):
    def must_tenant(self) -> bool:
        return must_tenant()

    def get_queryset(self) -> "QuerySet[BusinessArea]":
        if self.must_tenant():
            active_tenant = get_selected_tenant()
            return super().get_queryset().filter(id=active_tenant.hope_id)
        return super().get_queryset()


class BusinessArea(HopeModel):
    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=False)
    code = models.CharField(max_length=10, unique=True)
    long_name = models.CharField(max_length=255)
    region_code = models.CharField(max_length=8)
    region_name = models.CharField(max_length=8)

    objects = BusinessAreaManager()

    class Meta:
        db_table = "core_businessarea"
        ordering = ("name",)

    class Tenant:
        tenant_filter_field = "id"

    @cached_property
    def country_office(self) -> "CountryOffice":
        from hope_country_report.apps.core.models import CountryOffice

        return CountryOffice.objects.get(hope_id=self.id)

    def __str__(self) -> str:
        return str(self.name)
