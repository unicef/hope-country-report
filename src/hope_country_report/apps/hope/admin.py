from django.contrib import admin
from smart_admin.mixins import DisplayAllMixin
from hope_country_report.apps.hope.models import Household, Individual, BusinessArea


class ReadOnlyMixin:
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class HopeModelAdmin(ReadOnlyMixin, DisplayAllMixin, admin.ModelAdmin):
    pass


@admin.register(BusinessArea)
class BusinessAreaAdmin(HopeModelAdmin):
    pass


@admin.register(Household)
class HouseholdAdmin(HopeModelAdmin):
    pass


@admin.register(Individual)
class HouseholdAdmin(HopeModelAdmin):
    pass
