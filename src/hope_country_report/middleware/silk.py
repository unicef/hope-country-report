from typing import TYPE_CHECKING

from django.conf import settings

from flags.state import flag_enabled

if TYPE_CHECKING:
    from typing import Callable

    from django.http import HttpRequest, HttpResponse

try:
    from silk.middleware import SilkyMiddleware

    class SilkMiddleware(SilkyMiddleware):
        def __call__(self, request: "HttpRequest") -> "HttpResponse":
            if settings.DEBUG or flag_enabled("SILK_MIDDLEWARE", request=request):
                response = super().__call__(request)
            else:
                response = self.get_response(request)

            return response

except ImportError:

    class SilkMiddleware:  # type: ignore[no-redef]
        def __init__(self, get_response: "Callable[[HttpRequest],HttpResponse]") -> None:
            self.get_response = get_response

        def __call__(self, request: "HttpRequest") -> "HttpResponse":
            return self.get_response(request)
