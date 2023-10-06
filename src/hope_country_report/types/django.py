from typing import TypeAlias, TypeVar

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.db.models import Model

_M = TypeVar("_M", bound=Model)
_AnyUser: TypeAlias = AbstractBaseUser | AnonymousUser
