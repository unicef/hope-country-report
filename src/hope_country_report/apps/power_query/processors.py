from typing import Any, Dict, List, TYPE_CHECKING, Union

import io
import mimetypes
import re
from collections.abc import Callable, Iterable
from io import BytesIO

from django.db.models.query import QuerySet
from django.forms.models import model_to_dict
from django.template import Context, Template
from django.utils.functional import classproperty

import pdfkit
from pypdf import PdfReader, PdfWriter
from pypdf.constants import FieldFlag
from strategy_field.registry import Registry
from strategy_field.utils import fqn

from hope_country_report.apps.power_query.storage import DataSetStorage

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

    def normalize_dataset(
        self, dataset: Union[QuerySet, List[Dict[str, Any]], Dict[str, Any], Any]
    ) -> List[Dict[str, Any]]:
        if isinstance(dataset, QuerySet):
            return [model_to_dict(obj) for obj in dataset]
        elif isinstance(dataset, Iterable) and not isinstance(dataset, dict):
            return [model_to_dict(obj) for obj in dataset]
        elif isinstance(dataset, dict):
            return [dataset]
        elif hasattr(dataset, "dict") and callable(getattr(dataset, "dict", None)):
            return [row for row in dataset.dict()]
        else:
            raise ValueError("Unsupported dataset type")

    def process(self, context: "Dict[str, Any]") -> "ProcessorResult":
        tpl = self.formatter.template
        new_values: List[Dict[str, Any]] = []
        for entry in self.normalize_dataset(context["dataset"].data):
            new_entry = entry.copy()
            for key, value in entry.items():
                if isinstance(value, str) and image_pattern.search(value):
                    bitmap_key = f"{key}_bitmap"
                    new_entry[bitmap_key] = self.load_image_from_blob_storage(value)
            new_values.append(new_entry)
        # Ensure each dictionary has all keys, adding missing ones with None
        all_keys = set().union(*(d.keys() for d in new_values))
        for entry in new_values:
            for key in all_keys:
                entry.setdefault(key, None)
        reader = PdfReader(tpl.doc)
        writer = PdfWriter()
        ds = to_dataset(new_values).dict
        for entry in ds:
            writer.append(reader)
            writer.update_page_form_field_values(writer.pages[-1], entry, flags=FieldFlag.READ_ONLY)

        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream.getvalue()

    def load_image_from_blob_storage(self, image_path):
        """
        Load an image from blob storage.

        Args:
        - image_path (str): Path to the image within blob storage.

        Returns:
        - Image data in a format that can be directly used (e.g., file-like object).
        """
        with DataSetStorage().open(image_path, "rb") as image_file:
            image_data = image_file.read()
        return image_data


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
