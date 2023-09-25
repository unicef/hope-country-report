from django import forms
from django.contrib import admin

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin
from smart_admin.mixins import DisplayAllMixin
from unicef_security.admin import UserAdminPlus as _UserAdminPlus

from hope_country_report.apps.core.models import CountryOffice, User, UserRole
from hope_country_report.apps.hope.models import BusinessArea


class ReportAdmin(DisplayAllMixin, ExtraButtonsMixin, admin.ModelAdmin):
    pass


@admin.register(User)
class UserAdminPlus(_UserAdminPlus):  # type: ignore
    pass


class UserRoleForm(forms.ModelForm):  # type: ignore
    country_office = forms.ModelChoiceField(queryset=CountryOffice.objects.all())

    class Meta:
        model = UserRole
        fields = "__all__"


@admin.register(UserRole)
class UserRoleAdmin(ReportAdmin):  # type: ignore
    list_display = ("user", "group", "country_office")
    list_filter = ("country_office",)
    form = UserRoleForm
    autocomplete_fields = ("user", "group", "country_office")


@admin.register(CountryOffice)
class CountryOfficeAdmin(ReportAdmin):  # type: ignore
    search_fields = ("name",)
    list_filter = ("active",)

    @button()
    def sync(self, request):
        CountryOffice.sync()
