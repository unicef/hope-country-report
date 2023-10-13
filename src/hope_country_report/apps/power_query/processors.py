from typing import TYPE_CHECKING

from io import BytesIO

from django.template import Context, Template
from django.utils.functional import classproperty

from strategy_field.registry import Registry

from .utils import to_dataset

if TYPE_CHECKING:
    from typing import Any, Dict

    from .models import Formatter, ReportTemplate

mimetype_map = {
    "csv": "text/csv",
    "html": "text/html",
    "json": "application/json",
    "txt": "text/plain",
    "xls": "application/vnd.ms-excel",
    "xml": "application/xml",
    "yaml": "text/yaml",
    "pdf": "application/pdf",
}


class ProcessorStrategy:
    mime_type: str = ""
    verboxe_name = ""

    def __init__(self, context: "Formatter"):
        self.formatter = context

    @classproperty
    def label(cls):
        return cls.verboxe_name or str(cls.__name__)

    @classproperty
    def content_type(cls):
        return mimetype_map[cls.mime_type]

    def process(self, context: "Dict[str, Any]"):
        raise NotImplementedError


class ToXLS(ProcessorStrategy):
    mime_type = "xls"

    def process(self, context: "Dict[str, Any]"):
        dt = to_dataset(context["dataset"].data)
        return dt.export("xls")


class ToJSON(ProcessorStrategy):
    mime_type = "json"

    def process(self, context: "Dict[str, Any]"):
        dt = to_dataset(context["dataset"].data)
        return dt.export("json")


class ToYAML(ProcessorStrategy):
    mime_type = "yaml"

    def process(self, context: "Dict[str, Any]"):
        dt = to_dataset(context["dataset"].data)
        return dt.export("yaml")


class ToHTML(ProcessorStrategy):
    mime_type = "html"

    def process(self, context: "Dict[str, Any]"):
        tpl = Template(self.formatter.code)
        return tpl.render(Context(context))


class ToWord(ProcessorStrategy):
    mime_type = "docx"

    def process(self, context: "Dict[str, Any]"):
        from docxtpl import DocxTemplate

        tpl: "ReportTemplate" = self.formatter.template

        doc = DocxTemplate(tpl.doc)
        doc.render(context)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.read()


class ToPDF(ProcessorStrategy):
    mime_type = "pdf"

    def process(self, context: "Dict[str, Any]"):
        from docxtpl import DocxTemplate

        tpl = self.formatter.template
        doc = DocxTemplate(tpl.doc.read("b"))
        context = {"company_name": "World company"}
        doc.render(context)
        doc.save("generated_doc.docx")


class ProcessorRegistry(Registry):
    pass


registry = ProcessorRegistry(ProcessorStrategy, label_attribute="label")
registry.register(ToWord)
registry.register(ToJSON)
registry.register(ToHTML)
registry.register(ToYAML)
registry.register(ToXLS)
registry.register(ToPDF)
