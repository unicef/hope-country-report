from typing import Any, Dict, List, TYPE_CHECKING

import io
import mimetypes
import re
from collections.abc import Callable
from io import BytesIO
from django.template import Context, Template
from django.utils.functional import classproperty
import fitz
import pdfkit
from pypdf import PdfReader, PdfWriter
from pypdf.constants import FieldFlag
from strategy_field.registry import Registry
from strategy_field.utils import fqn
from hope_country_report.apps.power_query.storage import DataSetStorage, HopeStorage

from .utils import to_dataset

if TYPE_CHECKING:
    from typing import Tuple

    from .models import Dataset, Formatter, ReportTemplate

    ProcessorResult = bytes | BytesIO

image_pattern = re.compile(r"\.(jpg|jpeg|png|JPG|JPEG|PNG)$", re.IGNORECASE)

mimetypes.add_type("text/vnd.yaml", ".yaml")
mimetypes.add_type("application/vnd.ms-excel", ".xls")
mimetypes.add_type("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx")
mimetypes.add_type("text/xml", ".xml")
mimetypes.add_type("application/x-zip-compressed", ".zip")

mimetype_map = {
    k: v
    for k, v in mimetypes.types_map.items()
    if k in [".csv", ".html", ".json", ".txt", ".xlsx", ".xls", ".xml", ".yaml", ".pdf", ".docx", ".png", ".zip"]
}

TYPE_LIST = 1
TYPE_DETAIL = 2
TYPE_BOTH = 3

TYPES = ((TYPE_LIST, "List"), (TYPE_DETAIL, "Detail"))


class ProcessorStrategy:
    file_suffix: str = ".txt"
    verbose_name = ""
    format: int
    needs_file: bool = False

    def __init__(self, context: "Formatter"):
        self.formatter = context

    def validate(self) -> None:
        pass

    @classproperty
    def label(cls) -> str:
        return cls.verbose_name or str(cls.__name__)

    @classproperty
    def content_type(cls) -> str:
        return mimetype_map[cls.file_suffix]

    def process(self, context: "Dict[str, Any]") -> "ProcessorResult":
        raise NotImplementedError


class ToXLS(ProcessorStrategy):
    file_suffix = ".xls"
    format = TYPE_LIST
    verbose_name = "Dataset to XLS"

    def process(self, context: "Dict[str, Any]") -> bytes:
        dt = to_dataset(context["dataset"].data)
        return dt.export("xls")


class ToXLSX(ProcessorStrategy):
    file_suffix = ".xlsx"
    format = TYPE_LIST
    verbose_name = "Dataset to XLSX"

    def process(self, context: "Dict[str, Any]") -> bytes:
        dt = to_dataset(context["dataset"].data)
        return dt.export("xlsx")


class ToJSON(ProcessorStrategy):
    file_suffix = ".json"
    format = TYPE_LIST
    verbose_name = "Dataset to JSON"

    def process(self, context: "Dict[str, Any]") -> "ProcessorResult":
        dt = to_dataset(context["dataset"].data)
        return dt.export("json").encode()


class ToCSV(ProcessorStrategy):
    file_suffix = ".csv"
    format = TYPE_LIST
    verbose_name = "Dataset to CSV"

    def process(self, context: "Dict[str, Any]") -> "ProcessorResult":
        dt = to_dataset(context["dataset"].data)
        return dt.export("csv").encode()


class ToYAML(ProcessorStrategy):
    file_suffix = ".yaml"
    format = TYPE_LIST
    verbose_name = "Dataset to YAML"

    def process(self, context: "Dict[str, Any]") -> "ProcessorResult":
        ds: "Dataset" = context["dataset"]
        dt = to_dataset(ds.data)
        return dt.export("yaml").encode()


class ToHTML(ProcessorStrategy):
    file_suffix = ".html"
    format = TYPE_BOTH
    verbose_name = "Render CODE"

    def process(self, context: "Dict[str, Any]") -> "ProcessorResult":
        if self.formatter.template:
            with self.formatter.template.doc.open("rb") as f:
                code = f.read()
        else:
            code = self.formatter.code
        tpl = Template(code)
        return tpl.render(Context(context)).encode()


class ToText(ProcessorStrategy):
    file_suffix = ".txt"
    format = TYPE_BOTH
    verbose_name = "To Textfile"

    def process(self, context: "Dict[str, Any]") -> "ProcessorResult":
        tpl = Template(self.formatter.code)
        return tpl.render(Context(context)).encode()


class ToWord(ProcessorStrategy):
    file_suffix = ".docx"
    format = TYPE_BOTH
    needs_file = True

    def process(self, context: "Dict[str, Any]") -> "ProcessorResult":
        from docxtpl import DocxTemplate

        tpl: "ReportTemplate" = self.formatter.template

        doc = DocxTemplate(tpl.doc)
        doc.render(context)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()


class ToPDF(ProcessorStrategy):
    file_suffix = ".pdf"
    format = TYPE_BOTH
    verbose_name = "Text To PDF"

    def process(self, context: "Dict[str, Any]") -> "ProcessorResult":
        tpl = Template(self.formatter.code)
        out = tpl.render(Context(context))
        return pdfkit.from_string(out)


class ToFormPDF(ProcessorStrategy):
    file_suffix = ".pdf"
    format = TYPE_DETAIL
    needs_file = True

    def process(self, context: "Dict[str, Any]") -> bytes:
        tpl = self.formatter.template
        reader = PdfReader(tpl.doc)
        writer = PdfWriter()

        ds = to_dataset(context["dataset"].data).dict

        for entry in ds:
            writer.append(reader)
            text_values = {k: v for k, v in entry.items() if not self.is_image_field(k)}
            writer.update_page_form_field_values(writer.pages[-1], text_values, flags=FieldFlag.READ_ONLY)

        temp_pdf_stream = io.BytesIO()
        writer.write(temp_pdf_stream)
        temp_pdf_stream.seek(0)

        document = fitz.open(stream=temp_pdf_stream, filetype="pdf")

        for entry in ds:
            for field, value in entry.items():
                if self.is_image_field(value):
                    page = document[0]
                    rect = self.get_image_rect(document, field)
                    if rect:
                        image_stream = self.load_image_from_blob_storage(value)
                        page.insert_image(rect, stream=image_stream)

        final_pdf_stream = io.BytesIO()
        document.save(final_pdf_stream)
        final_pdf_stream.seek(0)
        document.close()

        return final_pdf_stream.getvalue()

    def is_image_field(self, value):
        return isinstance(value, str) and image_pattern.search(value)

    def get_image_rect(self, document, field_name):
        for page_num in range(len(document)):
            page = document[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    print("Found widget:", widget.field_name, "Rect:", widget.rect)
                    return widget.rect
        print("Widget not found for field name:", field_name)
        return None

    def load_image_from_blob_storage(self, image_path):
        # Implement logic to retrieve the image from blob storage and return as a bytes stream
        # This example uses a file path, replace it with actual blob storage access
        with DataSetStorage().open(image_path, "rb") as img_file:
            return img_file.read()


class ProcessorRegistry(Registry):
    _choices: "List[Tuple[str, str]] | None"

    def get_name(self, entry: "ProcessorStrategy") -> str:
        return entry.label

    def as_choices(self, _filter: Callable[[type], bool] | None = None) -> "List[Tuple[str, str]]":
        if _filter:
            return sorted((str(fqn(klass)), self.get_name(klass)) for klass in self if _filter(klass))
        elif not self._choices:
            self._choices = sorted((fqn(klass), self.get_name(klass)) for klass in self)  # type: ignore[return-value]

        return self._choices


registry = ProcessorRegistry(ProcessorStrategy, label_attribute="label")
registry.register(ToCSV)
registry.register(ToFormPDF)
registry.register(ToHTML)
registry.register(ToJSON)
registry.register(ToPDF)
registry.register(ToWord)
registry.register(ToXLS)
registry.register(ToXLSX)
registry.register(ToYAML)
registry.register(ToText)
