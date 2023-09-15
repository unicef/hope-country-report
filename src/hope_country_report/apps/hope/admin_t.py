from typing import TYPE_CHECKING

from adminfilters.value import ValueFilter

from hope_country_report.apps.hope.models import Area, BusinessArea, Household, Individual
from tenant_admin.options import MainTenantModelAdmin, TenantModelAdmin

if TYPE_CHECKING:
    from django.db.models import Model
    from django.http import HttpRequest


class ReadOnlyMixin:
    def has_add_permission(self, request: "HttpRequest", obj: "Model | None" = None) -> bool:
        return False

    def has_delete_permission(self, request: "HttpRequest", obj: "Model | None" = None) -> bool:
        return False

    def has_change_permission(self, request: "HttpRequest", obj: "Model | None" = None) -> bool:
        return False


class HopeModelAdmin(ReadOnlyMixin, TenantModelAdmin):
    pass


class BusinessAreaAdmin(MainTenantModelAdmin):
    model = BusinessArea


class HouseholdAdmin(HopeModelAdmin):
    model = Household
    tenant_filter_field = "business_area"
    list_filter = (("unicef_id", ValueFilter),)


class IndividualAdmin(HopeModelAdmin):
    model = Individual
    tenant_filter_field = "household__business_area"
    search_fields = ("full_name",)
    list_filter = (("household__unicef_id", ValueFilter), "relationship")


class AreaAdmin(HopeModelAdmin):
    model = Area
    tenant_filter_field = "__none__"
    # search_fields = ("full_name",)
    # list_filter = (("household__unicef_id", ValueFilter), "relationship")
