from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect

if TYPE_CHECKING:
    from django.http import HttpRequest


def index(request: "HttpRequest") -> "HttpResponseRedirect":
    return HttpResponseRedirect("/t/")
