from django import forms

from hope_country_report.apps.core.models import User


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("timezone", "language")
