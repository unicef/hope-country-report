from typing import Any, Dict, List, Optional, TYPE_CHECKING

import io
import logging
import mimetypes
import re
from collections.abc import Callable
from io import BytesIO

from django.core.files.temp import NamedTemporaryFile
from django.template import Context, Template
from django.utils.functional import classproperty

import fitz
import pdfkit
from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.constants import AnnotationDictionaryAttributes, FieldDictionaryAttributes, FieldFlag
from pypdf.generic import ArrayObject
from sentry_sdk import capture_exception
from strategy_field.registry import Registry
from strategy_field.utils import fqn

from hope_country_report.apps.power_query.storage import DataSetStorage, HopeStorage

from hope_country_report.apps.power_query.utils import (
    get_field_rect,
    to_dataset,
    convert_pdf_to_image_pdf,
    insert_special_image,
)

logger = logging.getLogger(__name__)
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

    def process(self, context: Dict[str, Any]) -> bytes:
        tpl = self.formatter.template
        reader = PdfReader(tpl.doc)
        font_size = context.get("context", {}).get("font_size", 10)
        font_color = context.get("context", {}).get("font_color", "black")
        ds = to_dataset(context["dataset"].data).dict
        output_pdf = PdfWriter()
        for index, entry in enumerate(ds, start=1):
            with NamedTemporaryFile(suffix=".pdf", delete=True) as temp_pdf_file:
                writer = PdfWriter()
                text_values = {}
                special_values = {}
                images = {}
                try:
                    for page in reader.pages:
                        for annot in page.annotations:
                            annot = annot.get_object()
                            field_name = annot[FieldDictionaryAttributes.T]
                            if field_name in entry:
                                value = entry[field_name]
                                language = self.is_special_language_field(field_name)
                                if self.is_image_field(annot):
                                    rect = annot[AnnotationDictionaryAttributes.Rect]
                                    text_values[field_name] = None
                                    images[field_name] = [rect, value]
                                elif language:
                                    special_values[field_name] = {"value": value, "language": language}
                                else:
                                    text_values[field_name] = value
                except IndexError as exc:
                    capture_exception(exc)
                    logger.exception(exc)
                    raise
                writer.append(reader)
                writer.update_page_form_field_values(writer.pages[-1], text_values, flags=FieldFlag.READ_ONLY)
                output_stream = io.BytesIO()
                writer.write(output_stream)
                output_stream.seek(0)
                temp_pdf_file.write(output_stream.read())

                document = fitz.open(stream=output_stream.getvalue(), filetype="pdf")
                for field_name, text in special_values.items():
                    insert_special_image(document, field_name, text, font_size, font_color)
                for field_name, (rect, image_path) in images.items():
                    if image_path:
                        self.insert_external_image(document, field_name, image_path)
                    else:
                        logger.warning(f"Image not found for field: {field_name}")
                document.ez_save(temp_pdf_file.name, deflate_fonts=True, deflate_images=1, deflate=1)
                output_stream.seek(0)
                output_pdf.append_pages_from_reader(PdfReader(temp_pdf_file.name))
        output_stream = io.BytesIO()
        output_pdf.write(output_stream)
        output_stream.seek(0)
        fitz_pdf_document = fitz.open(stream=output_stream, filetype="pdf")

        # Convert the PDF to an image-based PDF
        image_pdf_bytes = convert_pdf_to_image_pdf(fitz_pdf_document, dpi=300)

        return image_pdf_bytes

    def insert_external_image(self, document: fitz.Document, field_name: str, image_path: str, font_size: int = 10):
        """
        Loads, resizes, and inserts an external image into the specified field.
        """
        rect, page_index = get_field_rect(document, field_name)
        if rect is None or page_index is None:
            logger.error(f"No valid rectangle or page index found for field {field_name}. Cannot insert image.")
            return
        page = document[page_index]
        try:
            image_stream = self.load_image_from_blob_storage(image_path)
            image = Image.open(image_stream).rotate(-90, expand=True)
            image.thumbnail((800, 600), Image.LANCZOS)
            output_stream = io.BytesIO()
            image.save(output_stream, format="PNG")
            output_stream.seek(0)
            for widget in page.widgets():
                if widget.field_name == field_name:
                    page.delete_widget(widget)
                    break  # Stop the loop once we find and remove the widget
            rotate = 0
            if image.height < image.width:
                rotate = 270
            page.insert_image(rect, stream=output_stream, keep_proportion=False, rotate=rotate)
        except Exception as e:
            logger.exception(e)
            capture_exception(e)
            page.insert_textbox(
                rect,
                "Image unreadable",
                color=(1, 0, 0),
                fontsize=font_size,
                fontname="helv",
                align=fitz.TEXT_ALIGN_CENTER,
            )

    def is_image_field(self, annot: ArrayObject) -> bool:
        """
        Checks if a given PDF annotation represents an image field.
        """
        return (
            annot.get(FieldDictionaryAttributes.FT) == "/Btn"
            and AnnotationDictionaryAttributes.P in annot
            and AnnotationDictionaryAttributes.AP in annot
        )

    def is_special_language_field(self, field_name: str) -> Optional[str]:
        """Extract language code from the field name if it exists."""
        special_language_suffixes = {"_ar": "arabic", "_bn": "bengali", "_ru": "cyrillic", "_bur": "burmese"}
        for suffix, lang_code in special_language_suffixes.items():
            if field_name.endswith(suffix):
                return lang_code
        return None

    def load_image_from_blob_storage(self, image_path: str) -> BytesIO:
        with HopeStorage().open(image_path, "rb") as img_file:
            return BytesIO(img_file.read())


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
