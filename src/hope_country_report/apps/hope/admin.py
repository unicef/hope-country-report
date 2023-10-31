from typing import TYPE_CHECKING

from collections.abc import Sequence

from django.contrib import admin

from admin_cursor_paginator import CursorPaginatorAdmin
from admin_extra_buttons.api import ExtraButtonsMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.combo import RelatedFieldComboFilter
from adminfilters.dates import DateRangeFilter
from adminfilters.json import JsonFieldFilter
from adminfilters.mixin import AdminFiltersMixin
from adminfilters.querystring import QueryStringFilter
from adminfilters.value import ValueFilter
from smart_admin.mixins import DisplayAllMixin

from . import models

if TYPE_CHECKING:
    from django.contrib.admin.options import _ListFilterT, _ModelT
    from django.db.models import Model, QuerySet
    from django.http import HttpRequest

    from ...types.http import AuthHttpRequest


class ReadOnlyMixin:
    def has_add_permission(self, request: "HttpRequest", obj: "Model | None" = None) -> bool:
        return False

    def has_delete_permission(self, request: "HttpRequest", obj: "Model | None" = None) -> bool:
        return False

    def has_change_permission(self, request: "HttpRequest", obj: "Model | None" = None) -> bool:
        return False


class CursorButtonMixin(ExtraButtonsMixin, CursorPaginatorAdmin):
    change_list_template = "admin/hope/change_list.html"


class HopeModelAdmin(ReadOnlyMixin, AdminFiltersMixin, DisplayAllMixin, CursorButtonMixin):  # type: ignore
    def has_module_permission(self, request: "HttpRequest") -> bool:
        return True
        # return super().has_module_permission(request)


@admin.register(models.BusinessArea)
class BusinessAreaAdmin(HopeModelAdmin):
    search_fields = ("name",)
    list_filter = ("active", "region_name")


class AutoBusinessAreaCol:
    def get_list_display(self, request: "AuthHttpRequest") -> Sequence[str]:
        base = super().get_list_display(request)
        # if "business_area" not in base:
        return ("business_area", *base)
        # return base

    def get_list_filter(self, request: "HttpRequest") -> "Sequence[_ListFilterT]":
        base = super().get_list_filter(request)
        return (("business_area", AutoCompleteFilter), *base)


@admin.register(models.Household)
class HouseholdAdmin(AutoBusinessAreaCol, HopeModelAdmin):
    list_display = (
        "unicef_id",
        "withdrawn",
        "size",
        "first_registration_date",
    )
    list_filter = (
        ("unicef_id", ValueFilter),
        "withdrawn",
        QueryStringFilter,
        ("admin_area", AutoCompleteFilter),
        ("flex_fields", JsonFieldFilter),
        ("first_registration_date", DateRangeFilter),
    )


@admin.register(models.Individual)
class IndividualAdmin(AutoBusinessAreaCol, HopeModelAdmin):
    list_filter = (
        ("unicef_id", ValueFilter),
        QueryStringFilter,
        ("flex_fields", JsonFieldFilter),
        ("first_registration_date", DateRangeFilter),
        "relationship",
    )


@admin.register(models.Program)
class ProgramAdmin(AutoBusinessAreaCol, HopeModelAdmin):
    list_display = ("name", "status", "start_date", "end_date", "description", "sector")
    search_fields = ("name",)
    list_filter = (
        "status",
        ("business_area", RelatedFieldComboFilter),
        "sector",
    )


@admin.register(models.Cycle)
class CycleAdmin(HopeModelAdmin):
    list_display = ("program", "status", "start_date", "end_date")
    list_filter = ("status",)
    search_fields = ("name",)


@admin.register(models.Country)
class CountryAdmin(HopeModelAdmin):
    search_fields = ("name",)


@admin.register(models.AreaType)
class AreaTypeAdmin(HopeModelAdmin):
    list_display = ("name", "country", "parent", "area_level")
    list_filter = (
        ("country", AutoCompleteFilter),
        ("level", ValueFilter),
    )

    def get_queryset(self, request: "HttpRequest") -> "QuerySet[_ModelT]":
        return super().get_queryset(request).select_related("country", "parent")


@admin.register(models.Area)
class AreaAdmin(HopeModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "parent", "area_type")
    list_filter = (
        ("area_type__country", AutoCompleteFilter),
        ("area_type__level", ValueFilter),
    )

    def get_queryset(self, request: "HttpRequest") -> "QuerySet[_ModelT]":
        return super().get_queryset(request).select_related("parent", "area_type")


#
# @admin.register(models.IndividualRoleInHousehold)
# class IndividualRoleInHouseholdAdmin(HopeModelAdmin):
#     ...
#
# @admin.register(models.Document)
# class DocumentsAdmin(HopeModelAdmin):
#     ...
