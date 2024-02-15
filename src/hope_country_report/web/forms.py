from django import forms

from django_select2.forms import Select2Widget

from hope_country_report.apps.core.models import User


class UserProfileForm(forms.ModelForm[User]):
    class Meta:
        model = User
        fields = ("timezone", "language", "date_format", "time_format")
        widgets = {"timezone": Select2Widget}


class RequestAccessForm(forms.Form):
    message = forms.CharField(
        label="",
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "I would like to access"}),
    )
