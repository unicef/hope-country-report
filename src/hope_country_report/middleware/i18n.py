import locale

from django.utils import translation

from sos.utils.i18n import get_default_language, set_timezone


class UserLanguageMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        set_timezone(request)

        lang = get_default_language(request)
        request.selected_language = lang

        translation.activate(lang)

        locale.setlocale(locale.LC_ALL, "")
        response = self.get_response(request)
        response["AAAAAA"] = lang
        # if request.COOKIES.get("language") != lang:
        #     response.set_cookie("language", lang)
        return response
