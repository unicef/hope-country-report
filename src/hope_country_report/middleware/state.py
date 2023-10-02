import logging

from sos.state import state

logger = logging.getLogger(__name__)


class StateMiddleware:
    """Middleware that puts the request object in thread local storage."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        state.request = request
        response = self.get_response(request)
        state.set_cookies(response)
        state.request = None
        state.cookies = {}
        return response
