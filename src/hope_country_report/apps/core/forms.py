from django import forms

from .models import CountryOffice


class CountryOfficeForm(forms.ModelForm):
    class Meta:
        model = CountryOffice

        fields = [
            "locale",
            "timezone",
        ]
