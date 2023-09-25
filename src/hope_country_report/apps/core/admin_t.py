from admin_extra_buttons.decorators import button

from hope_country_report.apps.core.models import CountryOffice
from tenant_admin.options import TenantModelAdmin


class CountryOfficeAdmin(TenantModelAdmin):
    model = CountryOffice
    tenant_filter_field = "__none__"
    list_display = (
        "name",
        "active",
    )
    search_fields = ("name",)
    list_filter = ("active",)

    @button()
    def sync(self, request):
        CountryOffice.sync()

    # def get_writeable_fields(self, request, obj=None):
    #     return list(self.writeable_fields) + list(self.get_exclude(request, obj))
    #
    # def get_readonly_fields(self, request, obj=None):
    #     return []
    #
    # def has_change_permission(self, request, obj=None):
    #     return True
