from typing import Any, Dict, TYPE_CHECKING

import base64
import binascii
import datetime
import hashlib
import io
import json
import logging
from collections.abc import Callable, Iterable
from functools import wraps
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.contrib.auth import authenticate
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils.safestring import mark_safe

import fitz
import qrcode
import tablib
from constance import config
from PIL import ExifTags, Image, ImageDraw, ImageFont
from sentry_sdk import capture_exception, configure_scope

if TYPE_CHECKING:
    from hope_country_report.types.django import AnyModel


logger = logging.getLogger(__name__)


def is_valid_template(filename: Path) -> bool:
    if filename.suffix not in [".docx", ".pdf"]:
        return False
    if filename.stem.startswith("~"):
        return False
    return not filename.stem.startswith(".")


def make_naive(value: datetime.datetime) -> datetime.datetime:
    if isinstance(value, datetime.datetime) and value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None:
        return value.astimezone(datetime.UTC).replace(tzinfo=None)
    return value


def to_dataset(result: "QuerySet[AnyModel]|Iterable[Any]|tablib.Dataset|Dict[str,Any]") -> tablib.Dataset:  # noqa
    if isinstance(result, QuerySet):
        data = tablib.Dataset()
        fields = result.__dict__["_fields"]
        if not fields:
            fields = [field.name for field in result.model._meta.concrete_fields]
        data.headers = fields
        try:
            for obj in result.using(settings.POWER_QUERY_DB_ALIAS).all()[: config.PQ_SAMPLE_PAGE_SIZE]:
                line = []
                for f in fields:
                    if isinstance(obj, tuple):
                        line.append(str(obj))
                    elif isinstance(obj, datetime.datetime):
                        line.append(make_naive(obj))
                    else:
                        line.append(str(getattr(obj, f)))
                data.append(line)
        except Exception as e:
            logger.exception(e)
            raise
            # raise ValueError(f"Results can't be rendered as a tablib Dataset: {e}")
    elif isinstance(result, list | tuple):
        data = tablib.Dataset()
        fields = set().union(*(d.keys() for d in list(result)))
        data.headers = fields
        try:
            for obj in result:
                data.append([make_naive(obj[f]) if isinstance(obj[f], datetime.datetime) else obj[f] for f in fields])
        except Exception:
            raise ValueError("Results can't be rendered as a tablib Dataset")
    elif isinstance(result, tablib.Dataset | dict):
        data = result
    else:
        raise ValueError(f"{result} ({type(result)}")
    return data


def get_sentry_url(event_id: int, html: bool = False) -> str:
    url = f"{settings.SENTRY_URL}?query={event_id}"
    if html:
        return mark_safe('<a href="{url}" target="_sentry" >View on Sentry<a/>')
    return url


def basicauth(view: Callable[..., Callable]) -> Callable[..., Any]:
    def wrap(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return view(request, *args, **kwargs)

        if "HTTP_AUTHORIZATION" in request.META:
            try:
                auth = request.headers["Authorization"].split()
                if len(auth) == 2 and auth[0].lower() == "basic":
                    uname, passwd = base64.b64decode(auth[1].encode()).decode().split(":")
                    user = authenticate(username=uname, password=passwd)
                    if user is not None and user.is_active:
                        request.user = user
                        return view(request, *args, **kwargs)
            except binascii.Error:
                pass
        response = HttpResponse()
        response.status_code = 401
        response["WWW-Authenticate"] = 'Basic realm="HOPE"'
        return response

    return wrap


def sizeof(num: float, suffix: str = "") -> str:
    for unit in ["b", "Kb", "Mb", "Gb", "Tb", "Pb", "Eb", "Zb"]:
        if num % 1 == 0:
            n = f"{abs(num):.0f}"
        else:
            n = f"{num:3.1f}"
        if abs(num) < 1024.0:
            return f"{n} {unit}{suffix}".strip()
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}".strip()


def dict_hash(dictionary: dict[str, Any]) -> str:
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is
    # the same as {'b': 2, 'a': 1}
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()


def sentry_tags(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        with configure_scope() as scope:
            scope.set_tag("celery", True)
            scope.set_tag("celery_task", func.__name__)

            return func(*args, **kwargs)

    return wrapper


def load_font_for_language(language: str, font_size: int = 12) -> ImageFont.FreeTypeFont:
    """Returns the appropriate font for the given language."""
    # Base directory for fonts
    base_font_path = Path(settings.STATIC_ROOT) / "fonts"
    font_files = {
        "arabic": base_font_path / "NotoNaskhArabic-Bold.ttf",
        "cyrillic": base_font_path / "FreeSansBold.ttf",
        "bengali": base_font_path / "NotoSansBengali-Bold.ttf",
        "burmese": base_font_path / "NotoSerifMyanmar-Bold.ttf",
    }

    default_font = base_font_path / "FreeSansBold.ttf"
    font_path = font_files.get(language, default_font)
    return ImageFont.truetype(str(font_path), size=font_size)


def get_field_rect(document: fitz.Document, field_name: str) -> tuple[fitz.Rect, int] | None:
    """Returns the Rect and page index of the specified field."""
    for page_num in range(len(document)):
        page = document[page_num]
        for widget in page.widgets():
            if widget.field_name == field_name:
                if widget.field_type == 7:
                    widget.field_flags |= fitz.PDF_FIELD_IS_READ_ONLY
                    widget.update()
                return widget.rect, page_num
    return None, None


def insert_special_language_image(
    text: str, rect: fitz.Rect, language: str, dpi: int = 300, font_size: int = 10, font_color: str = "black"
) -> BytesIO:
    """Generate an image with text properly handled for special languages."""
    rect_width_in_inches = (rect.x1 - rect.x0) / 72
    rect_height_in_inches = (rect.y1 - rect.y0) / 72
    width = int(rect_width_in_inches * dpi)
    height = int(rect_height_in_inches * dpi)
    image = Image.new("RGBA", (width, height), (28, 171, 231, 0))
    draw = ImageDraw.Draw(image)
    font_size_scaled = int(font_size * dpi / 72)
    font = load_font_for_language(language, font_size_scaled)

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    draw.text((x, y), text, font=font, fill=font_color)

    # Save the image to a bytes buffer
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format="PNG", optimize=True)
    img_byte_arr.seek(0)

    return img_byte_arr.getvalue()


def convert_pdf_to_image_pdf(pdf_document: fitz.Document, dpi: int = 300) -> bytes:
    """
    Converts each page of a PDF document to an image and then creates a new PDF
    with these images as its pages.
    """
    new_pdf_document = fitz.open()

    for page_num in range(pdf_document.page_count):  # Use .page_count here
        pix = pdf_document[page_num].get_pixmap(dpi=dpi)
        new_page = new_pdf_document.new_page(width=pix.width, height=pix.height)
        new_page.insert_image(fitz.Rect(0, 0, pix.width, pix.height), pixmap=pix)

    new_pdf_bytes = BytesIO()
    new_pdf_document.save(new_pdf_bytes, deflate_fonts=1, deflate_images=1, deflate=1)
    new_pdf_bytes.seek(0)
    return new_pdf_bytes.getvalue()


def insert_special_image(
    document: fitz.Document, field_name: str, text_info: dict, font_size: int = 10, font_color: str = "black"
) -> None:
    """
    Generates and inserts an image containing the given special non-Latin text into
    the specified field as an annotation.
    """
    text = text_info["value"]
    language = text_info["language"]
    rect, page_index = get_field_rect(document, field_name)
    if rect:
        image_stream = insert_special_language_image(text, rect, language, font_size=font_size, font_color=font_color)
        img_rect = fitz.Rect(*rect)
        page = document[page_index]
        page.insert_image(img_rect, stream=image_stream, keep_proportion=False)
    else:
        logger.info(f"Field {field_name} not found")


def insert_qr_code(document: fitz.Document, field_name: str, data: str, rect: fitz.Rect, page_index: int) -> None:
    """Generates a QR code and inserts it into the specified field."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_image = qr.make_image(fill_color="black", back_color="white")
    image_stream = io.BytesIO()
    qr_image.save(image_stream, format="PNG")
    image_stream.seek(0)

    page = document[page_index]

    for widget in page.widgets():
        if widget.field_name == field_name:
            page.delete_widget(widget)
            break

    page.insert_image(rect, stream=image_stream, keep_proportion=False)


def apply_exif_orientation(image: Image.Image) -> Image.Image:
    """Adjusts the image based on EXIF orientation metadata."""
    try:
        exif = image.getexif()
        if exif is not None:
            orientation = exif.get(ExifTags.TAGS.get("Orientation"))
            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)
    except Exception as e:
        logger.warning(f"Failed to apply EXIF orientation: {e}")
        capture_exception(e)
    return image
