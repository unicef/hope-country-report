from typing import TYPE_CHECKING

from django.shortcuts import render

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def index(request: "HttpRequest") -> "HttpResponse":
    return render(request, "home.html")
