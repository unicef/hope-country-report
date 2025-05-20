from typing import Any, TYPE_CHECKING

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from hope_country_report.config import env

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser
    from django.http import HttpRequest


class AnyUserAuthBackend(ModelBackend):
    def authenticate(
        self, request: "HttpRequest | None", username: str | None = None, password: str | None = None, **kwargs: Any
    ) -> "AbstractBaseUser | None":
        if settings.DEBUG:
            if username == env.get_value("ADMIN_EMAIL"):
                user, __ = get_user_model().objects.update_or_create(
                    username=username,
                    defaults={"is_staff": True, "is_active": True, "is_superuser": True},
                )
                assert user.is_active
                assert user.is_superuser
                return user
            if username.startswith("user"):
                user, __ = get_user_model().objects.update_or_create(
                    username=username,
                    defaults={
                        "is_staff": False,
                        "is_active": True,
                        "is_superuser": False,
                        "email": f"{username}@demo.org",
                    },
                )
                return user
            if username.startswith("admin"):
                user, __ = get_user_model().objects.update_or_create(
                    username=username,
                    defaults={
                        "is_staff": True,
                        "is_active": True,
                        "is_superuser": True,
                        "email": f"{username}@demo.org",
                    },
                )
                return user
        return None
