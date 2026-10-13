import io
import zipfile

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from hope_country_report.apps.power_query.validators import (
    MAX_TEMPLATE_SIZE,
    report_template_upload_to,
    validate_template_content,
    validate_template_extension,
    validate_template_size,
)


def _docx_bytes() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("word/document.xml", "<document/>")
    return buffer.getvalue()


def _upload(name: str, content: bytes = b"x") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, content)


@pytest.mark.parametrize("name", ["evil.html", "evil.svg", "archive.zip", "run.exe", "noext"])
def test_extension_rejected(name):
    with pytest.raises(ValidationError):
        validate_template_extension(_upload(name))


@pytest.mark.parametrize("name", ["template.docx", "template.pdf", "TEMPLATE.PDF"])
def test_extension_accepted(name):
    validate_template_extension(_upload(name))


def test_content_rejects_fake_pdf():
    with pytest.raises(ValidationError):
        validate_template_content(_upload("fake.pdf", b"<html>not a pdf</html>"))


def test_content_rejects_plain_zip_as_docx():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        z.writestr("notes.txt", "hi")
    with pytest.raises(ValidationError):
        validate_template_content(_upload("fake.docx", buffer.getvalue()))


def test_content_accepts_valid_docx():
    validate_template_content(_upload("ok.docx", _docx_bytes()))


def test_content_accepts_valid_pdf():
    validate_template_content(_upload("ok.pdf", b"%PDF-1.7\n..."))


def test_size_rejected():
    with pytest.raises(ValidationError):
        validate_template_size(_upload("big.docx", b"x" * (MAX_TEMPLATE_SIZE + 1)))


def test_upload_to_is_server_generated():
    path = report_template_upload_to(None, "client-controlled.docx")
    assert path.startswith("reporttemplate/")
    assert path.endswith(".docx")
    assert "client" not in path
