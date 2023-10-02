from typing import TYPE_CHECKING

from adminfilters.value import ValueFilter

from hope_country_report.apps.hope import models
from hope_country_report.apps.tenant.options import TenantModelAdmin

if TYPE_CHECKING:
    from django.db.models import Model

    from hope_country_report.types.http import AuthHttpRequest


class ReadOnlyMixin:
    def has_add_permission(self, request: "AuthHttpRequest", obj: "Model | None" = None) -> bool:
        return False

    def has_delete_permission(self, request: "AuthHttpRequest", obj: "Model | None" = None) -> bool:
        return False

    def has_change_permission(self, request: "AuthHttpRequest", obj: "Model | None" = None) -> bool:
        return False


class HopeModelAdmin(ReadOnlyMixin, TenantModelAdmin):
    pass


#
# class BusinessAreaAdmin(MainTenantModelAdmin):
#     model = models.BusinessArea
#


class HouseholdAdmin(HopeModelAdmin):
    model = models.Household
    tenant_filter_field = "business_area"
    list_filter = (("unicef_id", ValueFilter),)


#
# class IndividualAdmin(HopeModelAdmin):
#     model = models.Individual
#     tenant_filter_field = "household__business_area"
#     search_fields = ("full_name",)
#     list_filter = (("household__unicef_id", ValueFilter), "relationship")
#
#
# class AreaAdmin(HopeModelAdmin):
#     model = models.Area
#     tenant_filter_field = "__none__"
#     # search_fields = ("full_name",)
#     # list_filter = (("household__unicef_id", ValueFilter), "relationship")
#
#
class ProgramAdmin(HopeModelAdmin):
    model = models.Program
    tenant_filter_field = "business_area"
    # search_fields = ("full_name",)
    # list_filter = (("household__unicef_id", ValueFilter), "relationship")


#
# class DataCollectingTypeAdmin(HopeModelAdmin):
#     model = models.DataCollectingType
#     tenant_filter_field = "__none__"
#     # search_fields = ("full_name",)
#     # list_filter = (("household__unicef_id", ValueFilter), "relationship")
#
