from django.utils.functional import SimpleLazyObject

from sos.utils.user_agent import get_user_agent


class UserAgentMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        request.user_agent = SimpleLazyObject(lambda: get_user_agent(request))
        return self.get_response(request)
