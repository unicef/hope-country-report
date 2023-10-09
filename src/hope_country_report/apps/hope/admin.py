from typing import TYPE_CHECKING

from django.contrib import admin

from smart_admin.mixins import DisplayAllMixin

from . import models

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


class HopeModelAdmin(ReadOnlyMixin, DisplayAllMixin, admin.ModelAdmin):  # type: ignore
    def has_module_permission(self, request: "HttpRequest") -> bool:
        return True
        # return super().has_module_permission(request)


@admin.register(models.BusinessArea)
class BusinessAreaAdmin(HopeModelAdmin):
    search_fields = ("name",)
    list_filter = ("active", "region_name")


@admin.register(models.Household)
class HouseholdAdmin(HopeModelAdmin):
    pass


@admin.register(models.Individual)
class IndividualAdmin(HopeModelAdmin):
    pass


@admin.register(models.Program)
class ProgramAdmin(HopeModelAdmin):
    pass


@admin.register(models.Cycle)
class CycleAdmin(HopeModelAdmin):
    pass


@admin.register(models.Country)
class CountryAdmin(HopeModelAdmin):
    pass


@admin.register(models.Area)
class AreaAdmin(HopeModelAdmin):
    pass


@admin.register(models.AreaType)
class AreaTypeAdmin(HopeModelAdmin):
    pass


@admin.register(models.DataCollectingType)
class DataCollectingTypeAdmin(HopeModelAdmin):
    pass
