#  :copyright: Copyright (c) 2018-2020. OS4D Ltd - All Rights Reserved
#  :license: Commercial
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Written by Stefano Apostolico <s.apostolico@gmail.com>, November 2020
import logging
import sys

from django.contrib import messages
from django.http import HttpRequest, HttpResponseNotAllowed, HttpResponseRedirect, JsonResponse
from django.template.response import TemplateResponse
from django.utils.deprecation import MiddlewareMixin

from social_core.exceptions import AuthCanceled, AuthFailed, AuthForbidden
from sos.exceptions import RegistrationClosedError, RemoteAPIException
from sos.web.views.errors import error_405_view

logger = logging.getLogger(__name__)


class ExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request: "HttpRequest", exception: Exception):
        ret = None
        if isinstance(exception, (ConnectionError,)):
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                ret = JsonResponse({"error": "System not Available"}, status=00)
            ret = TemplateResponse(
                request,
                "_error_remote.html",
                context={"exception": exception},
                status=500,
            )

        # elif isinstance(exception, (AuthForbidden,)):
        #     ret = error_403_view(request, exception)
        elif isinstance(exception, (RegistrationClosedError,)):
            messages.error(request, str(exception))
            ret = HttpResponseRedirect("/")
        elif isinstance(exception, (AuthFailed, AuthCanceled, AuthForbidden)):
            logger.exception(exception, exc_info=sys.exc_info())
            # backend = getattr(request, "backend", None)
            # backend_name = getattr(backend, "name", "unknown-backend")
            messages.error(request, str(exception), extra_tags="social-auth " + exception.backend.name)
            ret = HttpResponseRedirect("/")
        elif isinstance(exception, (RemoteAPIException,)):
            logger.exception(exception, exc_info=sys.exc_info())
            ret = JsonResponse(
                {
                    "error": exception.__class__.__name__,
                    "code": exception.response.status_code,
                    "details": [{"type": "is-danger", "message": "Server Error"}],
                },
                status=500,
            )
        if ret:
            return ret
        raise exception

    def __call__(self, request):
        response = self.get_response(request)
        if isinstance(response, HttpResponseNotAllowed):
            return error_405_view(request)
        return response
