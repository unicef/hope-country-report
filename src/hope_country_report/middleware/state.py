import logging
from typing import TYPE_CHECKING

from django.http import HttpRequest, HttpResponse

from hope_country_report.state import state

if TYPE_CHECKING:
    from typing import Callable, TYPE_CHECKING

    from hope_country_report.types.http import _R

logger = logging.getLogger(__name__)


class StateMiddleware:
    def __init__(self, get_response: "Callable[[HttpRequest],HttpResponse]") -> None:
        self.get_response = get_response

    def __call__(self, request: "_R") -> "HttpResponse":
        state.request = request
        response = self.get_response(request)
        state.set_cookies(response)
        state.reset()
        return response
