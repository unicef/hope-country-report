from django import forms
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.templatetags.static import static
from strategy_field.forms import StrategyFormField

from ...state import state
from ..tenant.config import conf
from ..tenant.utils import get_selected_tenant
from .models import Dataset, Formatter, Query
from .processors import registry
from .widget import PythonFormatterEditor


class SelectDatasetForm(forms.Form):
    dataset = forms.ModelChoiceField(queryset=Dataset.objects)
    processor = StrategyFormField(registry=registry, choices=registry.as_choices())


class ExportForm(forms.Form):
    formatter = forms.ModelChoiceField(queryset=Formatter.objects)


class FormatterTestForm(forms.Form):
    dataset = forms.ModelChoiceField(Dataset.objects)


class ExplainQueryForm(forms.Form):
    target = forms.ModelChoiceField(
        queryset=ContentType.objects,
        required=True,
        blank=True,
        limit_choices_to={"app_label": "hope"},
    )
    query = forms.CharField(widget=PythonFormatterEditor)

    def __init__(self, *args, **kwargs) -> None:
        from django.contrib.contenttypes.models import ContentType

        super().__init__(*args, **kwargs)
        self.fields["target"].queryset = ContentType.objects.filter(app_label="hope").order_by("model")

    class Media:
        js = (
            static("admin/js/vendor/jquery/jquery.js"),
            static("admin/js/jquery.init.js"),
            static("admin/explain.js"),
        )


class QueryForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={"style": "width:80%"}))
    target = forms.ModelChoiceField(
        queryset=ContentType.objects,
        required=False,
        blank=True,
        limit_choices_to={"app_label": "hope"},
    )
    code = forms.CharField(widget=PythonFormatterEditor, required=False)
    owner = forms.ModelChoiceField(queryset=get_user_model().objects, widget=forms.HiddenInput, required=False)  # type: ignore
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2, "style": "width:80%"}))

    class Meta:
        model = Query
        exclude = ()

    def __init__(self, *args, **kwargs) -> None:
        from django.contrib.contenttypes.models import ContentType

        super().__init__(*args, **kwargs)
        self.fields["country_office"].queryset = conf.auth.get_allowed_tenants()
        self.fields["target"].queryset = ContentType.objects.filter(app_label="hope").order_by("model")

        if not self.instance or not self.instance.pk:
            self.initial["country_office"] = get_selected_tenant()
            self.initial["owner"] = state.request.user

    def clean_owner(self):
        if not self.cleaned_data.get("owner"):
            return state.request.user
        return self.cleaned_data.get("owner")
