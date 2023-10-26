from django import forms

import django_stubs_ext

from hope_country_report.apps.core.models import User

django_stubs_ext.monkeypatch()


class UserProfileForm(forms.ModelForm[User]):
    class Meta:
        model = User
        fields = ("timezone", "language")
