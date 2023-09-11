from typing import TYPE_CHECKING

from django.contrib import admin

from smart_admin.mixins import DisplayAllMixin

from hope_country_report.apps.hope.models import BusinessArea, Household, Individual

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
    pass


@admin.register(BusinessArea)
class BusinessAreaAdmin(HopeModelAdmin):
    pass


@admin.register(Household)
class HouseholdAdmin(HopeModelAdmin):
    pass


@admin.register(Individual)
class IndividualAdmin(HopeModelAdmin):
    pass
