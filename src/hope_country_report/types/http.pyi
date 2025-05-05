from typing import TypeVar

from django.http import HttpRequest, HttpResponse, HttpResponseBase, HttpResponseRedirect, StreamingHttpResponse

from admin_extra_buttons.utils import HttpResponseRedirectToReferrer

from hope_country_report.apps.core.models import User

AnyRequest = TypeVar("AnyRequest", bound=HttpRequest, covariant=True)
AnyResponse = TypeVar("AnyResponse", bound=HttpResponseBase, covariant=True)
RedirectOrResponse = HttpResponseRedirect | HttpResponseRedirectToReferrer | HttpResponse | StreamingHttpResponse

class AuthHttpRequest(HttpRequest):
    user: User
