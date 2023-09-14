from typing import TypeVar

from django.db.models import Model
from django.http import HttpRequest

from hope_country_report.apps.core.models import User

M = TypeVar("M", bound=Model)

class AuthHttpRequest(HttpRequest):
    user: User
