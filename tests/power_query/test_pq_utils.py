import datetime
from base64 import b64encode
from io import BytesIO
from pathlib import Path

import pytest
from unittest.mock import MagicMock

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.utils import timezone

import fitz
import tablib
from PIL import ExifTags, Image
from pytz import utc

from hope_country_report.apps.power_query.utils import (
    apply_exif_orientation,
    basicauth,
    convert_pdf_to_image_pdf,
    dict_hash,
    get_field_rect,
    get_font_url,
    get_sentry_url,
    insert_qr_code,
    insert_special_image,
    insert_special_language_image,
    is_valid_template,
    load_font_for_language,
    sentry_tags,
    sizeof,
    to_dataset,
)
from hope_country_report.utils.media import resource_path

TEST_PDF = resource_path("apps/power_query/doc_templates/program_receipt.pdf")


@pytest.fixture
def sample_pdf() -> fitz.Document:
    return fitz.open(TEST_PDF)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("a.docx", True),
        ("a.pdf", True),
        ("a.mov", False),
        ("~.pdf", False),
        (".a.pdf", False),
    ],
)
def test_is_valid_template(value, expected):
    assert is_valid_template(Path(value)) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (10, "10 b"),
        (1024, "1 Kb"),
        (1500, "1.5 Kb"),
        (1024**10, "1048576.0Yi"),
    ],
)
def test_sizeof(value, expected):
    assert sizeof(value) == expected


def test_to_dataset_qs(user):
    qs = type(user).objects.all()
    assert to_dataset(qs).width == 18  # number of fields
    assert sorted(to_dataset(qs).headers) == [
        "azure_id",
        "date_format",
        "date_joined",
        "display_name",
        "email",
        "first_name",
        "id",
        "is_active",
        "is_staff",
        "is_superuser",
        "job_title",
        "language",
        "last_login",
        "last_name",
        "password",
        "time_format",
        "timezone",
        "username",
    ]


def test_to_dataset_values(user):
    qs = type(user).objects.values_list("username")
    assert str(to_dataset(qs)) == "username             \n---------------------\n('user@example.com',)"


def test_to_dataset_iterable(user):
    qs = type(user).objects.values("pk")
    assert to_dataset(list(qs))


def test_to_dataset_dataset():
    data = tablib.Dataset([1, 2])
    assert to_dataset(data)


def test_to_dataset_error():
    with pytest.raises(ValueError):
        assert to_dataset("")


test_data = [
    ("queryset_values_list", "date_joined", "%Y-%m-%d %H:%M:%S"),
    ("iterable", "event_time", "%Y-%m-%d %H:%M:%S"),
]


@pytest.mark.parametrize("test_type, field_name, expected_format", test_data)
def test_to_dataset_tzinfo(test_type, field_name, expected_format, user):
    tz_aware_datetime = timezone.make_aware(datetime.datetime(2023, 3, 15, 12, 0))
    if test_type == "queryset_values_list":
        user.date_joined = tz_aware_datetime
        user.save()
        data = type(user).objects.filter(id=user.pk).values_list(field_name, flat=True)
    else:  # iterable
        data = [{field_name: tz_aware_datetime}]
    dataset = to_dataset(data)
    expected_naive_datetime_str = tz_aware_datetime.astimezone(utc).replace(tzinfo=None).strftime(expected_format)
    found = any(expected_naive_datetime_str in ",".join(map(str, row)) for row in dataset)
    assert found, f"Expected datetime string '{expected_naive_datetime_str}' not found in dataset."


def test_basicauth(rf):
    request = rf.get("/")
    request.user = AnonymousUser()
    view = basicauth(lambda request: HttpResponse("Ok"))
    response = view(request)
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


def test_basicauth_authenticate(rf, user):
    request = rf.get(
        "/",
        headers={"Authorization": "Basic " + b64encode(f"{user.username}:password".encode()).decode("ascii")},
    )

    request.user = AnonymousUser()
    view = basicauth(lambda request: HttpResponse("Ok"))
    response = view(request)
    assert response.status_code == 200


def test_basicauth_authenticated(rf, user):
    request = rf.get("/")
    request.user = user
    view = basicauth(lambda request: HttpResponse("Ok"))
    response = view(request)
    assert response.status_code == 200


def test_basicauth_authenticate_fail(rf, user):
    request = rf.get(
        "/",
        headers={"Authorization": "Basic " + b64encode(f"{user.username}:".encode()).decode("ascii")},
    )

    request.user = AnonymousUser()
    view = basicauth(lambda request: HttpResponse("Ok"))
    response = view(request)
    assert response.status_code == 401


@pytest.mark.parametrize("value", ["abc", "Basic abc", ""])
def test_basicauth_authenticate_wrong_header(rf, user, value):
    request = rf.get("/", headers={"Authorization": value})

    request.user = AnonymousUser()
    view = basicauth(lambda request: HttpResponse("Ok"))
    response = view(request)
    assert response.status_code == 401


@pytest.mark.parametrize("html", [True, False])
def test_get_sentry_url(html):
    assert get_sentry_url(123, html)


def test_sentry_tags():
    with MagicMock() as func:
        func.__name__ = "func"
        sentry_tags(func)()
        assert func.call_count == 1


def test_get_field_rect(sample_pdf: fitz.Document) -> None:
    rect, page_index = get_field_rect(sample_pdf, "Programma")
    assert rect is not None
    assert page_index == 0


def test_insert_special_language_image(mocked_responses):
    from hope_country_report.apps.power_query import utils

    utils._font_cache.clear()
    expected_font_name = "NotoNaskhArabic-Bold.ttf"
    font_url = get_font_url(expected_font_name)

    font_file_path = resource_path(f"web/static/fonts/{expected_font_name}")
    with open(font_file_path, "rb") as f:
        font_content = f.read()

    mocked_responses.add(
        "GET",
        font_url,
        body=font_content,
        status=200,
    )
    text = "الافترايفكتس و البريمير و الافد ميدا كومبوزر"
    rect = fitz.Rect(0, 0, 200, 200)
    language = "arabic"
    dpi = 300
    image_data = insert_special_language_image(text, rect, language, dpi)
    image = Image.open(BytesIO(image_data))
    assert image.size == (rect.width * dpi // 72, rect.height * dpi // 72)


def test_convert_pdf_to_image_pdf(sample_pdf):
    pdf_bytes = convert_pdf_to_image_pdf(sample_pdf)
    new_pdf = fitz.open("pdf", pdf_bytes)
    assert len(new_pdf) == 1


def test_insert_special_image(mocked_responses, sample_pdf: fitz.Document) -> None:
    from hope_country_report.apps.power_query import utils

    utils._font_cache.clear()
    expected_font_name = "NotoNaskhArabic-Bold.ttf"
    font_url = get_font_url(expected_font_name)

    font_file_path = resource_path(f"web/static/fonts/{expected_font_name}")
    with open(font_file_path, "rb") as f:
        font_content = f.read()

    mocked_responses.add(
        "GET",
        font_url,
        body=font_content,
        status=200,
    )
    text_info = {"value": "الافترايفكتس و البريمير و الافد ميدا كومبوزر", "language": "arabic"}
    field_name = "Cognome_ar"
    page = sample_pdf[0]

    insert_special_image(sample_pdf, field_name, text_info)

    annotations = list(page.annots())
    assert len(annotations) == 0, "No annotations found after insertion"


def test_insert_qr_code(sample_pdf):
    field_name = "code_qr"
    data = "https://example.com"
    page = sample_pdf[0]
    rect, page_index = get_field_rect(sample_pdf, field_name)

    if rect is not None and page_index is not None:
        insert_qr_code(sample_pdf, field_name, data, rect, page_index)
        page = sample_pdf[page_index]
        images = page.get_images(full=True)
        assert len(images) > 0, "No images found on the page, QR code insertion failed"
    else:
        pytest.fail("No valid rectangle or page index found for the field.")


def test_dict_hash():
    d1 = {"a": 1, "b": 2}
    d2 = {"b": 2, "a": 1}
    d3 = {"a": 1, "b": 3}
    assert dict_hash(d1) == dict_hash(d2)
    assert dict_hash(d1) != dict_hash(d3)


@pytest.mark.parametrize(
    "language, expected_font_name",
    [
        ("arabic", "NotoNaskhArabic-Bold.ttf"),
        ("cyrillic", "FreeSansBold.ttf"),
        ("bengali", "NotoSansBengali-Bold.ttf"),
        ("burmese", "NotoSerifMyanmar-Bold.ttf"),
        ("unknown_language", "FreeSansBold.ttf"),
    ],
)
def test_load_font_for_language(mocked_responses, language, expected_font_name):
    from hope_country_report.apps.power_query import utils

    utils._font_cache.clear()
    font_url = get_font_url(expected_font_name)

    font_file_path = resource_path(f"web/static/fonts/{expected_font_name}")
    with open(font_file_path, "rb") as f:
        font_content = f.read()

    mocked_responses.add(
        "GET",
        font_url,
        body=font_content,
        status=200,
    )

    font = load_font_for_language(language)
    assert font is not None
    assert len(mocked_responses.calls) == 1
    assert mocked_responses.calls[0].request.url == font_url


@pytest.mark.parametrize(
    "orientation, original_size, new_size",
    [
        (1, (100, 200), (100, 200)),  # No rotation
        (3, (100, 200), (100, 200)),  # 180 rotation
        (6, (100, 200), (200, 100)),  # 90 CW rotation
        (8, (100, 200), (200, 100)),  # 270 CW rotation
    ],
)
def test_apply_exif_orientation(orientation, original_size, new_size):
    image = Image.new("RGB", original_size, "white")
    exif = image.getexif()
    exif[ExifTags.TAGS.get("Orientation")] = orientation
    image.getexif = lambda: exif

    oriented_image = apply_exif_orientation(image)
    assert oriented_image.size == new_size


def test_apply_exif_orientation_no_exif():
    image = Image.new("RGB", (100, 200), "white")
    oriented_image = apply_exif_orientation(image)
    assert oriented_image.size == (100, 200)
