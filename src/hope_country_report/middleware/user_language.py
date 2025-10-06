import logging
from typing import TYPE_CHECKING

from django.utils import translation

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.http import HttpRequest, HttpResponse

    from hope_country_report.types.http import AuthHttpRequest

logger = logging.getLogger(__name__)


class UserLanguageMiddleware:
    def __init__(self, get_response: "Callable[[HttpRequest],HttpResponse]") -> None:
        self.get_response = get_response

    def __call__(self, request: "AuthHttpRequest") -> "HttpResponse":
        user = request.user
        if user.is_authenticated and user.language:
            language = user.language
        else:
            language = translation.get_language_from_request(request, check_path=False)

        translation.activate(language)
        return self.get_response(request)
