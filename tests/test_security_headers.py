import re

from csp.middleware import CSPMiddleware
from django.conf import settings
from django.http import HttpResponse
from django.middleware.security import SecurityMiddleware
from django.test import override_settings

_SENTINEL = {
    "SECURE_HSTS_SECONDS": 31536000,
    "SECURE_HSTS_INCLUDE_SUBDOMAINS": True,
    "SECURE_HSTS_PRELOAD": True,
    "SECURE_REFERRER_POLICY": "strict-origin-when-cross-origin",
    "SECURE_CONTENT_TYPE_NOSNIFF": True,
}


@override_settings(**_SENTINEL)
def test_security_settings_are_configured():
    assert settings.SECURE_HSTS_SECONDS >= 31536000
    assert settings.SECURE_HSTS_INCLUDE_SUBDOMAINS is True
    assert settings.SECURE_HSTS_PRELOAD is True
    assert settings.SECURE_REFERRER_POLICY == "strict-origin-when-cross-origin"
    assert settings.SECURE_CONTENT_TYPE_NOSNIFF is True
    assert "django.middleware.security.SecurityMiddleware" in settings.MIDDLEWARE
    assert "csp.middleware.CSPMiddleware" in settings.MIDDLEWARE
    assert settings.CONTENT_SECURITY_POLICY["DIRECTIVES"].get("default-src")


@override_settings(**_SENTINEL)
def test_hsts_header_is_sent(rf):
    request = rf.get("/")
    request.is_secure = lambda: True
    response = SecurityMiddleware(lambda r: HttpResponse("ok"))(request)

    match = re.search(r"max-age=(\d+)", response["Strict-Transport-Security"])
    assert match and int(match.group(1)) >= 31536000
    assert "includeSubDomains" in response["Strict-Transport-Security"]
    assert "preload" in response["Strict-Transport-Security"]


@override_settings(**_SENTINEL)
def test_referrer_policy_and_nosniff_headers_are_sent(rf):
    request = rf.get("/")
    request.is_secure = lambda: True
    response = SecurityMiddleware(lambda r: HttpResponse("ok"))(request)

    assert response["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert response["X-Content-Type-Options"] == "nosniff"


def test_csp_header_is_sent(rf):
    request = rf.get("/")
    response = CSPMiddleware(lambda r: HttpResponse("ok"))(request)

    assert response["Content-Security-Policy"]
    assert "default-src" in response["Content-Security-Policy"]
