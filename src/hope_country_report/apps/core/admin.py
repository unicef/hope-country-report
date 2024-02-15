from typing import Any, Optional, TYPE_CHECKING

from django import forms
from django.contrib import admin
from django.db.models.fields.json import JSONField
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from jsoneditor.forms import JSONEditor
from leaflet.admin import LeafletGeoAdmin
from smart_admin.mixins import DisplayAllMixin
from unicef_security.admin import UserAdminPlus as _UserAdminPlus

from hope_country_report.apps.core.models import CountryOffice, CountryShape, User, UserRole

if TYPE_CHECKING:
    from hope_country_report.types.http import AuthHttpRequest


class BaseAdmin(DisplayAllMixin, ExtraButtonsMixin, admin.ModelAdmin):  # type: ignore[type-arg]
    pass


@admin.register(User)
class UserAdmin(_UserAdminPlus):  # type: ignore
    fieldsets = (
        (None, {"fields": (("username", "azure_id"), "password")}),
        (
            _("Preferences"),
            {
                "fields": (
                    (
                        "language",
                        "timezone",
                    ),
                    ("date_format", "time_format"),
                )
            },
        ),
        (
            _("Personal info"),
            {
                "fields": (
                    (
                        "first_name",
                        "last_name",
                    ),
                    ("email", "display_name"),
                    ("job_title",),
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    def get_fieldsets(self, request: HttpRequest, obj: Optional[Any] = None) -> Any:
        if not request.user.is_superuser:
            return super().get_fieldsets(request, obj)
        return _UserAdminPlus.fieldsets


class UserRoleForm(forms.ModelForm):  # type: ignore
    country_office = forms.ModelChoiceField(queryset=CountryOffice.objects)

    class Meta:
        model = UserRole
        fields = "__all__"


@admin.register(UserRole)
class UserRoleAdmin(AdminFiltersMixin, BaseAdmin):
    list_display = ("user", "group", "country_office")
    list_filter = (
        ("country_office", AutoCompleteFilter),
        ("group", AutoCompleteFilter),
        ("user", AutoCompleteFilter),
    )
    # form = UserRoleForm
    autocomplete_fields = ("user", "group", "country_office")


@admin.register(CountryOffice)
class CountryOfficeAdmin(AdminFiltersMixin, BaseAdmin):
    list_display = ("name", "active", "code", "slug", "shape")
    search_fields = ("name",)
    list_filter = ("active", "region_code")
    formfield_overrides = {
        JSONField: {
            "widget": JSONEditor(
                init_options={"mode": "view", "modes": ["view", "code", "tree"]},
                ace_options={"readOnly": False},
            )
        }
    }
    readonly_fields = ("hope_id",)
    autocomplete_fields = ("shape",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("shape")

    @button()
    def sync(self, request: "AuthHttpRequest") -> None:
        CountryOffice.objects.sync()


@admin.register(CountryShape)
class CountryShapeAdmin(LeafletGeoAdmin):
    list_display = ("name", "area", "iso2", "iso3", "un", "region", "subregion")
    search_fields = ("name", "iso3")
