from typing import TypeVar

from django.db.models import Model
from django.http import HttpRequest, HttpResponse

from hope_country_report.apps.core.models import User

_R = TypeVar("_R", bound=HttpRequest)
AnyResponse = TypeVar("AnyResponse", bound=HttpResponse, covariant=True)

class AuthHttpRequest(HttpRequest):
    user: User
