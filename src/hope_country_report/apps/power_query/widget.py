from typing import Any

from django import forms
from django.templatetags.static import static


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
