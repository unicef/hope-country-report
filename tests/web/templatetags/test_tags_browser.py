import pytest

from hope_country_report.web.templatetags.browser import is_media_supported


@pytest.mark.parametrize("ct", ["text/csv", "application/pdf", "text/html", "image/png"])
def test_is_media_supported(ct, rf):
    context = {"request": rf.get("/", HTTP_ACCEPT=["*/*"])}
    assert is_media_supported(context, ct) in [True, False]
