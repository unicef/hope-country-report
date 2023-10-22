from typing import TYPE_CHECKING

import logging

from django.http import HttpRequest, HttpResponse

from hope_country_report.apps.tenant.utils import RequestHandler

if TYPE_CHECKING:
    from typing import Callable, TYPE_CHECKING

    from hope_country_report.types.http import AuthHttpRequest

logger = logging.getLogger(__name__)


class StateSetMiddleware:
    def __init__(self, get_response: "Callable[[HttpRequest],HttpResponse]") -> None:
        self.get_response = get_response
        self.handler = RequestHandler()

    def __call__(self, request: "AuthHttpRequest") -> "HttpResponse":
        self.handler.process_request(request)
        response = self.get_response(request)
        return response


class StateClearMiddleware:
    def __init__(self, get_response: "Callable[[HttpRequest],HttpResponse]") -> None:
        self.get_response = get_response
        self.handler = RequestHandler()

    def __call__(self, request: "AuthHttpRequest") -> "HttpResponse":
        response = self.get_response(request)
        self.handler.process_response(request, response)

        return response
