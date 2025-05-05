from typing import TYPE_CHECKING

import logging

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse

from hope_country_report.apps.power_query.exceptions import RequestablePermissionDenied
from hope_country_report.apps.power_query.models import ReportConfiguration, ReportDocument
from hope_country_report.apps.tenant.exceptions import InvalidTenantError, SelectTenantException

if TYPE_CHECKING:
    from collections.abc import Callable

    from hope_country_report.types.http import AuthHttpRequest

logger = logging.getLogger(__name__)


class ExceptionMiddleware:
    def __init__(self, get_response: "Callable[[HttpRequest],HttpResponse]") -> None:
        self.get_response = get_response

    def process_exception(self, request: "AuthHttpRequest", exception: BaseException) -> HttpResponse:
        if isinstance(exception, PermissionDenied):
            return HttpResponseForbidden()
        if isinstance(exception, RequestablePermissionDenied):
            if isinstance(exception.object, ReportConfiguration):
                obj = exception.object
            elif isinstance(exception.object, ReportDocument):
                obj = exception.object.report
            else:
                return HttpResponseForbidden()
            return HttpResponseRedirect(reverse("request-access", args=[obj.country_office.slug, obj.pk]))
        if isinstance(exception, SelectTenantException | InvalidTenantError):
            response = HttpResponseRedirect(reverse("admin:login"))
            response.set_cookie("select", "1")
            return response
        raise exception

    def __call__(self, request: "AuthHttpRequest") -> "HttpResponse":
        return self.get_response(request)
