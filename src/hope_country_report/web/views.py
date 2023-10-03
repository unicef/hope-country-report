from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect
from django.shortcuts import render

if TYPE_CHECKING:
    from django.http import HttpRequest


def index(request: "HttpRequest") -> "HttpResponseRedirect":
    return render(request, "home.html")
