from typing import TypeVar

from django.db.models import Model
from django.http import HttpRequest, HttpResponse

from hope_country_report.apps.core.models import User

AnyRequest = TypeVar("AnyRequest", bound=HttpRequest, covariant=True)
AnyResponse = TypeVar("AnyResponse", bound=HttpResponse, covariant=True)

class AuthHttpRequest(HttpRequest):
    user: User
