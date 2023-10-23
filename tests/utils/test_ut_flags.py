import pytest
from unittest import mock

from django.core.exceptions import ValidationError
from django.http import HttpRequest

from hope_country_report.utils.flags import debug, hostname, server_ip, superuser, validate_bool


@pytest.mark.parametrize("value", ["true", "1", "yes", "t", "y", "false", "0", "no", "f", "n"])
def test_validate_bool(value):
    try:
        validate_bool(value)
    except Exception as exc:
        pytest.fail(f"{value}' raised an exception {exc}")


@pytest.mark.parametrize("value", ["a", "9"])
def test_validate_bool_fail(value):
    with pytest.raises(ValidationError):
        assert validate_bool(value)


@pytest.mark.parametrize("value", ["t", "tRue", "yes", "1"])
def test_superuser(rf, value, admin_user):
    request = rf.get("/")
    request.user = admin_user
    assert superuser(value, request)


@pytest.mark.parametrize("value", ["t", "tRue", "yes", "1"])
def test_debug(settings, value):
    settings.DEBUG = True
    assert debug(value)


def test_server_ip(rf):
    request = rf.get("/", REMOTE_ADDR="192.168.66.66")
    assert server_ip("192.168.66.66", request)


@pytest.mark.parametrize("value", ["myserver.com", "myserver.com:888", "myserver.com:443"])
def test_hostname(value, rf):
    request: HttpRequest = rf.get("/", SERVER_NAME=value)
    with mock.patch("django.http.HttpRequest.get_host", lambda x: value):
        assert hostname("myserver.com", request)
