import logging
from typing import TYPE_CHECKING

from django.http import HttpRequest, HttpResponse

if TYPE_CHECKING:
    from typing import Callable, TYPE_CHECKING

    from hope_country_report.types.http import _R

logger = logging.getLogger(__name__)


class TenantMiddleware:
    def __init__(self, get_response: "Callable[[HttpRequest],HttpResponse]") -> None:
        self.get_response = get_response

    def __call__(self, request: "_R") -> "HttpResponse":
        # tenant = get_tenant_from_request(request)
        # state.tenant = tenant
        response = self.get_response(request)
        return response
