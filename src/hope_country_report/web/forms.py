from django import forms

import django_stubs_ext
from django_select2.forms import Select2Widget

from hope_country_report.apps.core.models import User

django_stubs_ext.monkeypatch()


class UserProfileForm(forms.ModelForm[User]):
    class Meta:
        model = User
        fields = ("timezone", "language", "date_format", "time_format")
        widgets = {"timezone": Select2Widget}
