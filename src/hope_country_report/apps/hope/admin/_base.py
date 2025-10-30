from typing import TYPE_CHECKING

from admin_cursor_paginator import CursorPaginatorAdmin
from admin_extra_buttons.api import ExtraButtonsMixin
from adminfilters import filters as extra_filters
from adminfilters.mixin import AdminFiltersMixin
from django.contrib import admin
from django.contrib.admin import ListFilter
from django.db import models
from smart_admin.mixins import DisplayAllMixin

if TYPE_CHECKING:
    from django.db import Model

    from hope_country_report.types.http import AnyRequest, AuthHttpRequest


class ReadOnlyMixin:
    def has_add_permission(self, request: "AuthHttpRequest", obj: "Model | None" = None) -> bool:
        return False

    def has_delete_permission(self, request: "AuthHttpRequest", obj: "Model | None" = None) -> bool:
        return False

    def has_change_permission(self, request: "AuthHttpRequest", obj: "Model | None" = None) -> bool:
        return False


class CursorButtonMixin(ExtraButtonsMixin, CursorPaginatorAdmin):
    change_list_template = "admin/hope/change_list.html"


def get_filters_for_model(model: "type[Model]", only_index: bool = True) -> list[str | ListFilter]:
    ret = [extra_filters.QueryStringFilter]
    for field in model._meta.fields:
        if only_index and not (field.db_index or field.unique):
            continue
        if isinstance(field, models.CharField):
            ret.append((field.name, extra_filters.ValueFilter))
        if isinstance(field, models.BooleanField | models.DateField | models.DateTimeField):
            ret.append(field.name)
        elif isinstance(field, models.ForeignKey):
            ret.append((field.name, extra_filters.AutoCompleteFilter))
        else:
            pass
    return ret


class AutoFiltersMixin(admin.ModelAdmin):
    def get_list_filter(self, request: "AnyRequest"):
        if self.list_filter == ["__auto__"]:
            return get_filters_for_model(self.model)
        if self.list_filter:
            return super().get_list_filter(request)
        return get_filters_for_model(self.model)


class HopeModelAdmin(ReadOnlyMixin, AdminFiltersMixin, AutoFiltersMixin, DisplayAllMixin, CursorButtonMixin):
    save_as = False
    save_as_continue = False
    list_filter = []

    def __str__(self) -> str:
        return f"{self.opts.app_label}.{self.__class__.__name__}"

    def has_module_permission(self, request: "AnyRequest") -> bool:
        return True
        # return super().has_module_permission(request)


class AutoRegisteredHopeModelAdmin(HopeModelAdmin):
    list_filter = ["__auto__"]
