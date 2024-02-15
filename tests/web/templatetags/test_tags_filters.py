from hope_country_report.web.templatetags.filters import build_filter_url


def test_build_filter_url_empty(rf):
    request = rf.get("/")
    ctx = {"request": request}
    assert build_filter_url(ctx, "tag") == "?"


def test_build_filter_url_remove(rf):
    request = rf.get("/?tag=1&active=0")
    ctx = {"request": request}
    assert build_filter_url(ctx, "tag") == "?active=0"


def test_build_filter_url_change(rf):
    request = rf.get("/?tag=1&active=0")
    ctx = {"request": request}
    assert build_filter_url(ctx, "tag", 2) == "?active=0&tag=2"
