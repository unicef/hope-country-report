from typing import Any, Optional, TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser
    from django.http import HttpRequest


class AnyUserAuthBackend(ModelBackend):
    def authenticate(
        self, request: "Optional[HttpRequest]", username: str | None = None, password: str | None = None, **kwargs: Any
    ) -> "AbstractBaseUser | None":
        if username:
            user, __ = get_user_model().objects.update_or_create(
                username=username,
                is_staff=True,
                is_active=True,
                is_superuser=True,
                email=f"{username}@demo.org",
            )
            return user
        return None
