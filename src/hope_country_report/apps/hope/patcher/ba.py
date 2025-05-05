from typing import TYPE_CHECKING

from hope_country_report.apps.hope.models import BusinessArea, BusinessareaCountries, Country
from hope_country_report.apps.hope.patcher import add_m2m
from hope_country_report.apps.tenant.db import TenantManager
from hope_country_report.apps.tenant.utils import get_selected_tenant, must_tenant

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from hope_country_report.apps.core.models import CountryOffice


class BusinessAreaManager(TenantManager["BusinessArea"]):
    def must_tenant(self) -> bool:
        return must_tenant()

    def get_queryset(self) -> "QuerySet[BusinessArea]":
        if self.must_tenant():
            active_tenant = get_selected_tenant()
            return super().get_queryset().filter(id=active_tenant.hope_id)
        return super().get_queryset()


BusinessArea._meta.local_managers = []
BusinessAreaManager().contribute_to_class(BusinessArea, "objects")
# BusinessArea._meta.default_manager = BusinessArea.objects


def country_office(self: BusinessArea) -> "CountryOffice":
    from hope_country_report.apps.core.models import CountryOffice

    return CountryOffice.objects.get(hope_id=self.id)


BusinessArea.country_office = property(country_office)
# BusinessArea.country_office = cached_property(country_office).__set_name__(BusinessArea, "country_office")

# models.ManyToManyField(AuthGroup,
#                        through=AuthUserGroups,
#                        ).contribute_to_class(AuthUser, 'groups')

add_m2m(BusinessArea, "countries", Country, BusinessareaCountries)
