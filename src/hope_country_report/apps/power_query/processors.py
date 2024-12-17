from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

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

from hope_country_report.apps.power_query.utils import (
    apply_exif_orientation,
    convert_pdf_to_image_pdf,
    get_field_rect,
    insert_qr_code,
    insert_special_image,
    to_dataset,
)

from ..core.storage import get_hope_storage

logger = logging.getLogger(__name__)
if TYPE_CHECKING:
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
    """
    Produce reports in PDF form or cards.
    This class handles PDF generation with special attention to QR code fields.
    """

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
                qr_codes = {}

                for page in reader.pages:
                    for annot in page.annotations:
                        annot = annot.get_object()
                        field_name = annot[FieldDictionaryAttributes.T]
                        if field_name in entry:
                            value = entry[field_name]
                            language = self.is_special_language_field(field_name)
                            if field_name.endswith("_qr"):
                                qr_codes[field_name] = value
                            elif self.is_image_field(annot):
                                rect = annot[AnnotationDictionaryAttributes.Rect]
                                images[field_name] = (rect, value)
                            elif language:
                                special_values[field_name] = {"value": value, "language": language}
                            else:
                                text_values[field_name] = value

                writer.append(reader)
                writer.update_page_form_field_values(writer.pages[-1], text_values, flags=FieldFlag.READ_ONLY)
                output_stream = io.BytesIO()
                writer.write(output_stream)
                output_stream.seek(0)
                temp_pdf_file.write(output_stream.read())

                # Open processed document for image and QR code insertion
                document = fitz.open(stream=output_stream.getvalue(), filetype="pdf")
                self.insert_images_and_qr_codes(document, images, qr_codes, special_values, font_size, font_color)
                document.save(temp_pdf_file.name)
                output_stream.seek(0)
                output_pdf.append_pages_from_reader(PdfReader(temp_pdf_file.name))

        output_stream = io.BytesIO()
        output_pdf.write(output_stream)
        output_stream.seek(0)

        fitz_pdf_document = fitz.open("pdf", output_stream.read())
        return convert_pdf_to_image_pdf(fitz_pdf_document, dpi=300)

    def insert_images_and_qr_codes(
        self,
        document: fitz.Document,
        images: Dict[str, Tuple[fitz.Rect, str]],
        qr_codes: Dict[str, str],
        special_values: Dict[str, Dict[str, str]],
        font_size: int,
        font_color: str,
    ):
        """
        Inserts images and QR codes into the specified fields.
        """
        for field_name, text in special_values.items():
            insert_special_image(document, field_name, text, int(font_size), font_color)
        for field_name, (rect, image_path) in images.items():
            self.insert_external_image(document, field_name, image_path, rect)
        for field_name, data in qr_codes.items():
            rect, page_index = get_field_rect(document, field_name)
            insert_qr_code(document, field_name, data, rect, page_index)

    def insert_external_image(
        self, document: fitz.Document, field_name: str, image_path: str, font_size: int = 10
    ) -> None:
        """
        Loads, resizes, adjusts DPI, and inserts an external image into the specified field.
        Automatically detects orientation using EXIF metadata and adjusts rotation.
        """
        rect: Optional[fitz.Rect]
        page_index: Optional[int]

        rect, page_index = get_field_rect(document, field_name)
        if rect is None or page_index is None:
            logger.error(f"No valid rectangle or page index found for field {field_name}. Cannot insert image.")
            return

        page = document[page_index]

        try:
            image_stream = self.load_image_from_blob_storage(image_path)
            image = Image.open(image_stream)
            image = apply_exif_orientation(image)
            pdf_width_in_inches = rect.width / 72.0
            pdf_height_in_inches = rect.height / 72.0
            target_dpi = 300
            image = image.resize(
                (int(pdf_width_in_inches * target_dpi), int(pdf_height_in_inches * target_dpi)),
                Image.LANCZOS,
            )
            output_stream = io.BytesIO()
            image.save(output_stream, format="PNG", dpi=(target_dpi, target_dpi))
            output_stream.seek(0)
            for widget in page.widgets():
                if widget.field_name == field_name:
                    page.delete_widget(widget)
                    break
            page.insert_image(rect, stream=output_stream, keep_proportion=True)

        except Exception as e:
            capture_exception(e)
            logger.warning(f"Image for field '{field_name}' is missing or invalid. Generating placeholder.")
            try:
                placeholder_width = int(rect.width)
                placeholder_height = int(rect.height)
                placeholder_image = Image.new("RGB", (placeholder_width, placeholder_height), color="cyan")
                placeholder_stream = io.BytesIO()
                placeholder_image.save(placeholder_stream, format="PNG")
                placeholder_stream.seek(0)
                page.insert_image(rect, stream=placeholder_stream, keep_proportion=True)
            except Exception as placeholder_error:
                capture_exception(placeholder_error)
                logger.error(f"Failed to insert placeholder image: {placeholder_error}")
                page.insert_textbox(
                    rect,
                    "Image not available",
                    color=(1.0, 0.0, 0.0),  # Red text
                    fontsize=font_size,
                    fontname="helv",
                    align=fitz.TEXT_ALIGN_CENTER,
                )

    def is_image_field(self, annot: ArrayObject) -> bool:
        """
        Checks if a given PDF annotation represents an image field.
        """
        return annot.get(FieldDictionaryAttributes.FT) == "/Btn" and AnnotationDictionaryAttributes.AP in annot

    def is_special_language_field(self, field_name: str) -> Optional[str]:
        """Extract language code from the field name if it exists."""
        special_language_suffixes = {"_ar": "arabic", "_bn": "bengali", "_ru": "cyrillic", "_bur": "burmese"}
        for suffix, lang_code in special_language_suffixes.items():
            if field_name.endswith(suffix):
                return lang_code
        return None

    def load_image_from_blob_storage(self, image_path: str) -> BytesIO:
        with get_hope_storage().open(image_path, "rb") as img_file:
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
