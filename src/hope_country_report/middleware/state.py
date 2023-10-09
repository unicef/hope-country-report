import logging
from typing import TYPE_CHECKING

from django.http import HttpRequest, HttpResponse

from hope_country_report.apps.tenant.utils import get_tenant_from_request
from hope_country_report.state import state

if TYPE_CHECKING:
    from typing import Callable, TYPE_CHECKING

    from hope_country_report.types.http import _R, AuthHttpRequest

logger = logging.getLogger(__name__)


class StateSetMiddleware:
    def __init__(self, get_response: "Callable[[HttpRequest],HttpResponse]") -> None:
        self.get_response = get_response

    def __call__(self, request: "AuthHttpRequest") -> "HttpResponse":
        state.request = request
        tenant = get_tenant_from_request(request)
        state.tenant = tenant

        response = self.get_response(request)
        return response


class StateClearMiddleware:
    def __init__(self, get_response: "Callable[[HttpRequest],HttpResponse]") -> None:
        self.get_response = get_response

    def __call__(self, request: "_R") -> "HttpResponse":
        response = self.get_response(request)

        state.set_cookies(response)
        state.reset()
        return response
