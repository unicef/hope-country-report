from typing import Callable, TYPE_CHECKING

import io
import mimetypes
from io import BytesIO

from django.template import Context, Template
from django.utils.functional import classproperty

import pdfkit
from pypdf import PdfReader, PdfWriter
from pypdf.constants import FieldFlag
from strategy_field.registry import Registry
from strategy_field.utils import fqn

from .utils import to_dataset

if TYPE_CHECKING:
    from typing import Any, Dict, List, Tuple

    from .models import Formatter, ReportTemplate

    ProcessorResult = bytes | BytesIO

# mimetypes = mimetypes.MimeTypes()
# mimetypes.add_type('application/xml', ".xml")

m = mimetypes.MimeTypes()
m.add_type("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx")

mimetype_map = {
    k: v
    for k, v in mimetypes.types_map.items()
    if k in [".csv", ".html", ".json", ".txt", ".xlsx", ".xml", ".yaml", ".pdf", ".docx", ".png"]
}

TYPE_LIST = 1
TYPE_DETAIL = 2
TYPE_BOTH = 3

TYPES = ((TYPE_LIST, "List"), (TYPE_DETAIL, "Detail"))


class ProcessorStrategy:
    mime_type: str | None = None
    verbose_name = ""
    format: int

    def __init__(self, context: "Formatter"):
        self.formatter = context

    def validate(self) -> None:
        pass

    @classproperty
    def label(cls) -> str:
        return cls.verbose_name or str(cls.__name__)

    @classproperty
    def content_type(cls) -> str:
        return mimetype_map[cls.mime_type]

    def process(self, context: "Dict[str, Any]") -> "ProcessorResult":
        raise NotImplementedError


class ToXLS(ProcessorStrategy):
    mime_type = ".xlsx"
    format = TYPE_LIST
    verbose_name = "Dataset to XLS"

    def process(self, context: "Dict[str, Any]") -> "ProcessorResult":
        dt = to_dataset(context["dataset"].data)
        return dt.export("xls")


class ToJSON(ProcessorStrategy):
    mime_type = ".json"
    format = TYPE_LIST
    verbose_name = "Dataset to JSON"

    def process(self, context: "Dict[str, Any]") -> "ProcessorResult":
        dt = to_dataset(context["dataset"].data)
        return dt.export("json")


class ToYAML(ProcessorStrategy):
    mime_type = ".yaml"
    format = TYPE_LIST
    verbose_name = "Dataset to YAML"

    def process(self, context: "Dict[str, Any]") -> "ProcessorResult":
        dt = to_dataset(context["dataset"].data)
        return dt.export("yaml")


class ToHTML(ProcessorStrategy):
    mime_type = None
    format = TYPE_BOTH
    verbose_name = "Render CODE"

    def process(self, context: "Dict[str, Any]") -> "ProcessorResult":
        tpl = Template(self.formatter.code)
        return tpl.render(Context(context)).encode()


class ToWord(ProcessorStrategy):
    mime_type = ".docx"
    format = TYPE_BOTH

    def process(self, context: "Dict[str, Any]") -> "ProcessorResult":
        from docxtpl import DocxTemplate

        tpl: "ReportTemplate" = self.formatter.template

        doc = DocxTemplate(tpl.doc)
        doc.render(context)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer


class ToPDF(ProcessorStrategy):
    mime_type = ".pdf"
    format = TYPE_BOTH

    def process(self, context: "Dict[str, Any]") -> "ProcessorResult":
        tpl = Template(self.formatter.code)
        out = tpl.render(Context(context))
        return pdfkit.from_string(out)


class ToFormPDF(ProcessorStrategy):
    mime_type = ".pdf"
    format = TYPE_DETAIL

    def process(self, context: "Dict[str, Any]") -> "ProcessorResult":
        tpl = self.formatter.template

        reader = PdfReader(tpl.doc)
        writer = PdfWriter()
        ds = to_dataset(context["dataset"].data).dict
        for entry in ds:
            writer.append(reader)
            writer.update_page_form_field_values(writer.pages[-1], entry, flags=FieldFlag.READ_ONLY)

        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream


class ProcessorRegistry(Registry):
    _choices: "List[Tuple[str, str]] | None"

    def get_name(self, entry: "ProcessorStrategy") -> str:
        return entry.label

    def as_choices(self, _filter: Callable[[type], bool] | None = None) -> "List[Tuple[str, str]]":
        if _filter:
            return sorted(
                (str(fqn(klass)), self.get_name(klass)) for klass in self if _filter(klass)
            )  # type: ignore[return-value]
        elif not self._choices:
            self._choices = sorted((fqn(klass), self.get_name(klass)) for klass in self)  # type: ignore[return-value]

        return self._choices


registry = ProcessorRegistry(ProcessorStrategy, label_attribute="label")
registry.register(ToWord)
registry.register(ToJSON)
registry.register(ToHTML)
registry.register(ToYAML)
registry.register(ToXLS)
registry.register(ToPDF)
registry.register(ToFormPDF)