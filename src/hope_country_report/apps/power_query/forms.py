from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.forms import Field

from ..tenant.config import conf
from ..tenant.utils import get_selected_tenant
from .models import Formatter, Query
from .widget import ContentTypeChoiceField, PythonFormatterEditor


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
    project = forms.ModelChoiceField(queryset=None, required=True, blank=False)

    class Meta:
        model = Query
        fields = ("name", "target", "description", "code")

    def __init__(self, *args, **kwargs) -> None:
        from django.contrib.contenttypes.models import ContentType

        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = conf.auth.get_allowed_tenants()
        self.fields["target"].queryset = ContentType.objects.filter(app_label="hope").order_by("model")

    def get_initial_for_field(self, field: Field, field_name: str) -> Any:
        if field_name == "project":
            return get_selected_tenant()
        return super().get_initial_for_field(field, field_name)
