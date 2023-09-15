from typing import Any, Dict, Optional, TYPE_CHECKING, Union

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.templatetags.static import static

if TYPE_CHECKING:
    from django.db.models.fields import _ChoicesCallable


class FormatterEditor(forms.Textarea):
    template_name = "power_query/widgets/codewidget.html"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        theme = kwargs.pop("theme", "midnight")
        super().__init__(*args, **kwargs)
        self.attrs["class"] = "formatter-editor"
        self.attrs["theme"] = theme

    class Media:
        css = {
            "all": (
                static("admin/power_query/codemirror/codemirror.css"),
                static("admin/power_query/codemirror/fullscreen.css"),
                static("admin/power_query/codemirror/foldgutter.css"),
                static("admin/power_query/codemirror/midnight.css"),
                static("admin/power_query/codemirror/abcdef.css"),
            )
        }
        js = (
            static("admin/power_query/codemirror/codemirror.js"),
            static("admin/power_query/codemirror/fullscreen.js"),
            static("admin/power_query/codemirror/active-line.js"),
            static("admin/power_query/codemirror/foldcode.js"),
            static("admin/power_query/codemirror/foldgutter.js"),
            static("admin/power_query/codemirror/indent-fold.js"),
            static("admin/power_query/codemirror/overlay.js"),
        )


class PythonFormatterEditor(FormatterEditor):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.attrs["class"] = "python-editor"

    class Media(FormatterEditor.Media):
        js = FormatterEditor.Media.js + (
            static("admin/power_query/codemirror/python.js"),
            static("admin/power_query/codemirror/django.js"),
        )


class ContentTypeChoiceField(forms.ModelChoiceField):
    def __init__(
        self,
        *,
        empty_label: str = "---------",
        required: bool = True,
        widget: Optional[Any] = None,
        label: Optional[Any] = None,
        initial: Optional[Any] = None,
        help_text: str = "",
        to_field_name: Optional[str] = None,
        limit_choices_to: Union[Union[Q, Dict[str, Any]], "_ChoicesCallable", None] = None,
        **kwargs: Any,
    ):
        queryset = ContentType.objects.order_by("model", "app_label")
        super().__init__(
            queryset,
            empty_label=empty_label,
            required=required,
            widget=widget,
            label=label,
            initial=initial,
            help_text=help_text,
            to_field_name=to_field_name,
            limit_choices_to=limit_choices_to,
            **kwargs,
        )

    def label_from_instance(self, obj: Any) -> str:
        return f"{obj.name.title()} ({obj.app_label})"
