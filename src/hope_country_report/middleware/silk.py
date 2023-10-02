from django.conf import settings

from flags.state import flag_enabled

try:
    from silk.middleware import SilkyMiddleware

    class SilkMiddleware(SilkyMiddleware):
        def __call__(self, request):
            if settings.DEBUG or flag_enabled("SILK_MIDDLEWARE", request=request):
                response = super().__call__(request)
            else:
                response = self.get_response(request)

            return response

except ImportError:

    class SilkMiddleware:
        def __init__(self, get_response):
            self.get_response = get_response

        def __call__(self, request):
            return self.get_response(request)
