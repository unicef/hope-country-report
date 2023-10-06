import logging
from typing import TYPE_CHECKING

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse

from hope_country_report.apps.tenant.exceptions import SelectTenantException

if TYPE_CHECKING:
    from typing import Callable, TYPE_CHECKING

    from hope_country_report.types.http import _R

logger = logging.getLogger(__name__)


class ExceptionMiddleware:
    def __init__(self, get_response: "Callable[[HttpRequest],HttpResponse]") -> None:
        self.get_response = get_response

    def process_exception(self, request, exception):
        if isinstance(exception, (SelectTenantException,)):
            return HttpResponseRedirect(reverse("admin:select_tenant"))
        else:
            raise exception

    def __call__(self, request: "_R") -> "HttpResponse":
        return self.get_response(request)
