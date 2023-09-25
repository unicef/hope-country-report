from typing import TypeVar

from django.db.models import Model

_M = TypeVar("_M", bound=Model)
