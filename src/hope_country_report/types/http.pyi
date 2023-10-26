from typing import TypeVar

from django.db.models import Model
from django.http import HttpRequest, HttpResponseBase

from hope_country_report.apps.core.models import User

AnyRequest = TypeVar("AnyRequest", bound=HttpRequest, covariant=True)
AnyResponse = TypeVar("AnyResponse", bound=HttpResponseBase, covariant=True)

class AuthHttpRequest(HttpRequest):
    user: User
