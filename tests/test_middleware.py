import pytest
from unittest.mock import MagicMock

from django.http import HttpResponse

from hope_country_report.apps.tenant.exceptions import InvalidTenantError, SelectTenantException
from hope_country_report.middleware.exception import ExceptionMiddleware
from hope_country_report.middleware.silk import SilkMiddleware
from hope_country_report.utils.flags import enable_flag


@pytest.fixture
def m():
    return ExceptionMiddleware(MagicMock())


def test_call(rf, m: ExceptionMiddleware):
    request = rf.get("/")
    get_response = MagicMock(side_effect=HttpResponse("Ok"))
    res = ExceptionMiddleware(get_response)(request)
    assert res == b"Ok"


@pytest.mark.parametrize("exc", [InvalidTenantError, SelectTenantException])
def test_process_exception_handle(rf, exc, m: ExceptionMiddleware):
    request = rf.get("/")
    response = m.process_exception(request, exc())
    assert response.status_code == 302


def test_process_exception_raise(rf, m: ExceptionMiddleware):
    request = rf.get("/")
    with pytest.raises(ValueError):
        m.process_exception(request, ValueError())


def test_silkmiddleware_enabled(rf):
    m = SilkMiddleware(MagicMock())
    request = rf.get("/")
    try:
        with enable_flag("SILK_PROFILING"):
            m(request)
    except Exception as e:
        pytest.fail(f"Unespected Exception raised: {e}")


def test_silkmiddleware_disabled(rf):
    m = SilkMiddleware(MagicMock())
    request = rf.get("/")
    try:
        m(request)
    except Exception as e:
        pytest.fail(f"Unespected Exception raised: {e}")
