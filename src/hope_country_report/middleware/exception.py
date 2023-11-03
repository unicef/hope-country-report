from typing import TYPE_CHECKING

import logging

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse

from hope_country_report.apps.tenant.exceptions import InvalidTenantError, SelectTenantException

if TYPE_CHECKING:
    from typing import TYPE_CHECKING

    from collections.abc import Callable

    from hope_country_report.types.http import AuthHttpRequest

logger = logging.getLogger(__name__)


class ExceptionMiddleware:
    def __init__(self, get_response: "Callable[[HttpRequest],HttpResponse]") -> None:
        self.get_response = get_response

    def process_exception(self, request: "AuthHttpRequest", exception: BaseException) -> HttpResponseRedirect:
        if isinstance(exception, (SelectTenantException, InvalidTenantError)):
            response = HttpResponseRedirect(reverse("admin:login"))
            response.set_cookie("select", "1")
            return response
        else:
            raise exception

    def __call__(self, request: "AuthHttpRequest") -> "HttpResponse":
        return self.get_response(request)
