from typing import TYPE_CHECKING

from flags.state import flag_enabled

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

from silk.middleware import SilkyMiddleware


class SilkMiddleware(SilkyMiddleware):
    def __call__(self, request: "HttpRequest") -> "HttpResponse":
        if flag_enabled("SILK_PROFILING", request=request):
            response = super().__call__(request)
        else:
            response = self.get_response(request)

        return response
