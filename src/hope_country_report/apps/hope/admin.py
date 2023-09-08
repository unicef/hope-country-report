from django.contrib import admin

from hope_country_report.apps.hope.models import Household


class ReadOnlyMixin:
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Household)
class HouseholdAdmin(ReadOnlyMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "unicef_id",
        "withdrawn",
    )
