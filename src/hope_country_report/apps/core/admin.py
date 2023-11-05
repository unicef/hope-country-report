from typing import TYPE_CHECKING

from django import forms
from django.contrib import admin
from django.db.models.fields.json import JSONField
from django.utils.translation import gettext_lazy as _

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from jsoneditor.forms import JSONEditor
from smart_admin.mixins import DisplayAllMixin
from unicef_security.admin import UserAdminPlus as _UserAdminPlus

from hope_country_report.apps.core.models import CountryOffice, User, UserRole

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
    search_fields = ("name",)
    list_filter = ("active",)
    formfield_overrides = {
        JSONField: {
            "widget": JSONEditor(
                init_options={"mode": "view", "modes": ["view", "code", "tree"]},
                ace_options={"readOnly": True},
            )
        }
    }

    @button()
    def sync(self, request: "AuthHttpRequest") -> None:
        CountryOffice.sync()
