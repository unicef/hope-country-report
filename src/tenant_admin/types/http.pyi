from typing import TypeVar

from django.db.models import Model
from django.http import HttpRequest

from hope_country_report.apps.core.models import User

_M = TypeVar("_M", bound=Model)
_R = TypeVar("_R", bound=HttpRequest)

class AuthHttpRequest(HttpRequest):
    user: User
