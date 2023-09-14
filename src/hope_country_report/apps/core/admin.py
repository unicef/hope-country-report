from django import forms
from django.contrib import admin

from smart_admin.mixins import DisplayAllMixin
from unicef_security.admin import UserAdminPlus as _UserAdminPlus

from hope_country_report.apps.core.models import User, UserRole
from hope_country_report.apps.hope.models import BusinessArea


@admin.register(User)
class UserAdminPlus(_UserAdminPlus):  # type: ignore
    pass


class UserRoleForm(forms.ModelForm):  # type: ignore
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all())

    class Meta:
        model = UserRole
        fields = "__all__"

    def clean_business_area(self) -> str:
        return str(self.cleaned_data["business_area"].pk)


@admin.register(UserRole)
class UserRoleAdmin(DisplayAllMixin, admin.ModelAdmin):  # type: ignore
    form = UserRoleForm
    autocomplete_fields = ("user", "group")
