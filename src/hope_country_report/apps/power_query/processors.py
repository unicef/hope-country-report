from typing import Any, Dict, List, Optional, TYPE_CHECKING

import io
import logging
import mimetypes
import re
from collections.abc import Callable
from datetime import datetime
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.temp import NamedTemporaryFile
from django.template import Context, Template
from django.utils.functional import classproperty

import fitz
import pdfkit
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from pypdf.constants import AnnotationDictionaryAttributes, FieldDictionaryAttributes, FieldFlag
from sentry_sdk import capture_exception
from strategy_field.registry import Registry
from strategy_field.utils import fqn

from hope_country_report.apps.power_query.storage import DataSetStorage, HopeStorage

from .utils import to_dataset

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

        ds = to_dataset(context["dataset"].data).dict
        output_pdf = PdfWriter()
        for index, entry in enumerate(ds, start=1):
            with NamedTemporaryFile(suffix=".pdf", delete=True) as temp_pdf_file:
                writer = PdfWriter()
                writer.append(reader)
                for field_name, value in entry.items():
                    if not value:  # Check for empty values
                        entry[field_name] = " "  # Insert a space
                text_values = {k: v for k, v in entry.items() if not self.is_arabic_field(v)}
                writer.update_page_form_field_values(writer.pages[-1], text_values, flags=FieldFlag.READ_ONLY)

                values = {}
                images = {}
                for page in reader.pages:
                    for annot in page.annotations:
                        annot = annot.get_object()
                        field_name = annot[FieldDictionaryAttributes.T]
                        if field_name in entry:
                            value = entry[field_name]
                            if self.is_image_field(value) and value:
                                rect = annot[AnnotationDictionaryAttributes.Rect]
                                images[field_name] = [rect, value]
                            else:
                                if isinstance(value, datetime):
                                    value = value.strftime("%Y-%m-%d")
                                values[field_name] = str(value)
                try:  # Load, insert, and save
                    output_stream = io.BytesIO()
                    writer.write(output_stream)
                    output_stream.seek(0)
                    temp_pdf_file.write(output_stream.read())
                except IndexError as exc:
                    capture_exception(exc)
                    logger.exception(exc)
                    raise

                document = fitz.open(stream=output_stream.getvalue(), filetype="pdf")
                page = document[0]
                for field_name, text in entry.items():
                    if self.is_arabic_field(text):
                        rect = self.get_field_rect(document, field_name)
                        if rect:
                            image_stream = self.generate_arabic_image(text, rect)
                            img_rect = fitz.Rect(*rect)
                            page.insert_image(img_rect, stream=image_stream, keep_proportion=False)
                for field_name, (rect, image_path) in images.items():
                    img_rect = fitz.Rect(*rect)
                    image_stream = self.load_image_from_blob_storage(image_path)
                    image = Image.open(image_stream).rotate(-90, expand=True)
                    output_stream = io.BytesIO()
                    image.save(output_stream, format="png", optimize=True)
                    output_stream.seek(0)
                    page.insert_image(img_rect, stream=output_stream, keep_proportion=False)
                document.ez_save(temp_pdf_file.name, deflate_fonts=1, deflate_images=1, deflate=1)
                output_stream.seek(0)
                output_pdf.append_pages_from_reader(PdfReader(temp_pdf_file.name))
        output_stream = io.BytesIO()
        output_pdf.write(output_stream)
        output_stream.seek(0)
        return output_stream.getvalue()

    def is_image_field(self, value: str) -> bool:
        return isinstance(value, str) and image_pattern.search(value)

    def load_image_from_blob_storage(self, image_path: str) -> BytesIO:
        with HopeStorage().open(image_path, "rb") as img_file:
            return BytesIO(img_file.read())

    def get_field_rect(self, document: fitz.Document, field_name: str) -> Optional[fitz.Rect]:
        for page_num in range(len(document)):
            page = document[page_num]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    return widget.rect
        return None

    def is_arabic_field(self, value: str) -> bool:
        arabic_pattern = re.compile("[\u0600-\u06FF]")
        return isinstance(value, str) and arabic_pattern.search(value)

    def generate_arabic_image(self, text: str, rect: fitz.Rect, dpi: int = 300) -> BytesIO:
        font_size = 10
        rect_width_in_inches = (rect.x1 - rect.x0) / 72
        rect_height_in_inches = (rect.y1 - rect.y0) / 72
        # Generate the image
        width = int(rect_width_in_inches * dpi)
        height = int(rect_height_in_inches * dpi)
        image = Image.new("RGBA", (width, height), (28, 171, 231, 0))
        draw = ImageDraw.Draw(image)
        font_size_scaled = int(font_size * dpi / 72)
        font_file_path = Path(settings.PACKAGE_DIR / "web" / "static" / "fonts" / "NotoNaskhArabic-Bold.ttf")
        font = ImageFont.truetype(font_file_path, font_size_scaled)

        # Calculate text size and position it in the center
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (width - text_width) / 2
        y = (height - text_height) / 2
        draw.text((x, y), text, font=font, fill="black", direction="rtl", align="right")

        # Save the image to a bytes buffer
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG", optimize=True)
        img_byte_arr.seek(0)

        return img_byte_arr.getvalue()


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
