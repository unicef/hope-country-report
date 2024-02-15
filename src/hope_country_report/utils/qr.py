import base64
import io
from pathlib import Path

import qrcode
from PIL import Image

from hope_country_report.utils.media import resource_path

UNDEFINED = object()


def bytes_to_data(data: bytes, ext: str = "png") -> str:
    base64_utf8_str = base64.b64encode(data).decode("utf-8")
    return f"data:image/{ext};base64,{base64_utf8_str}"


def image_to_data(img: Image) -> str:
    buff = io.BytesIO()
    img.save(buff, format="PNG")
    return bytes_to_data(buff.getvalue(), "png")


def get_file_as_data(p: Path) -> str:
    with p.open("rb") as f:
        data = f.read()

    ext = f.name.split(".")[-1]
    return bytes_to_data(data, ext)


def get_qrcode(content: str) -> bytes:
    logo_link = resource_path("web/static/unicef_logo.jpeg")

    logo = Image.open(logo_link)
    basewidth = 100
    wpercent = basewidth / float(logo.size[0])
    hsize = int(float(logo.size[1]) * float(wpercent))
    logo = logo.resize((basewidth, hsize), Image.LANCZOS)
    QRcode = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    QRcode.add_data(content)
    QRcode.make()
    QRimg = QRcode.make_image(fill_color="black", back_color="white").convert("RGB")

    # set size of QR code
    pos = ((QRimg.size[0] - logo.size[0]) // 2, (QRimg.size[1] - logo.size[1]) // 2)
    QRimg.paste(logo, pos)
    buff = io.BytesIO()
    # save the QR code generated
    QRimg.save(buff, format="PNG")
    return buff.getvalue()
