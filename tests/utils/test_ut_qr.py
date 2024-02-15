import io

from PIL import Image

from hope_country_report.utils.media import resource_path
from hope_country_report.utils.qr import bytes_to_data, get_file_as_data, get_qrcode, image_to_data

TEST_IMAGE = resource_path("web/static/unicef_logo.jpeg")


def test_file_to_data():
    data = get_file_as_data(TEST_IMAGE)
    assert data.startswith("data:image/jpeg")


def test_image_to_data():
    data = image_to_data(Image.open(TEST_IMAGE))
    assert data.startswith("data:image/png")


def test_bytes_to_data():
    assert bytes_to_data(get_qrcode("test"))


def test_get_qrcode():
    image_data = get_qrcode("test")
    img = Image.open(io.BytesIO(image_data))
    assert img
