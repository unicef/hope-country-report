import uuid
import zipfile
from pathlib import Path

from django.core.exceptions import ValidationError

ALLOWED_TEMPLATE_EXTENSIONS = frozenset({".docx", ".pdf"})
MAX_TEMPLATE_SIZE = 10 * 1024 * 1024


def report_template_upload_to(instance, filename: str) -> str:
    """Server-generated storage path (never trust the client filename)."""
    return f"reporttemplate/{uuid.uuid4().hex}{Path(filename).suffix.lower()}"


def validate_template_extension(value) -> None:
    if Path(value.name).suffix.lower() not in ALLOWED_TEMPLATE_EXTENSIONS:
        raise ValidationError(
            "Unsupported template type. Only .docx and .pdf files are allowed.",
            code="invalid_extension",
        )


def validate_template_size(value) -> None:
    if value.size and value.size > MAX_TEMPLATE_SIZE:
        raise ValidationError(
            f"Template is too large (max {MAX_TEMPLATE_SIZE // (1024 * 1024)} MB).",
            code="file_too_large",
        )


def validate_template_content(value) -> None:
    """Check magic bytes / structure so the extension cannot be spoofed."""
    suffix = Path(value.name).suffix.lower()
    value.seek(0)
    head = value.read(512)
    value.seek(0)

    if suffix == ".pdf":
        if not head.startswith(b"%PDF-"):
            raise ValidationError("File is not a valid PDF.", code="invalid_content")
        return

    if suffix == ".docx":
        if head[:4] != b"PK\x03\x04":
            raise ValidationError("File is not a valid DOCX.", code="invalid_content")
        try:
            with zipfile.ZipFile(value) as archive:
                names = archive.namelist()
        except zipfile.BadZipFile:
            raise ValidationError("File is not a valid DOCX.", code="invalid_content")
        finally:
            value.seek(0)
        if "[Content_Types].xml" not in names or not any(n.startswith("word/") for n in names):
            raise ValidationError("File is not a valid DOCX.", code="invalid_content")
