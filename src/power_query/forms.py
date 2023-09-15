from django import forms
from django.contrib.auth import get_user_model

from power_query.models import Formatter, Query
from power_query.widget import ContentTypeChoiceField, PythonFormatterEditor


class ExportForm(forms.Form):
    formatter = forms.ModelChoiceField(queryset=Formatter.objects)  # type: ignore


class FormatterTestForm(forms.Form):
    query = forms.ModelChoiceField(Query.objects)  # type: ignore


class QueryForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={"style": "width:80%"}))
    target = ContentTypeChoiceField()
    code = forms.CharField(widget=PythonFormatterEditor)
    owner = forms.ModelChoiceField(queryset=get_user_model().objects, widget=forms.HiddenInput)  # type: ignore
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2, "style": "width:80%"}))

    class Meta:
        model = Query
        fields = ("name", "target", "description", "code")
