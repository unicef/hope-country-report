from typing import TYPE_CHECKING

import contextlib

from django.conf import settings
from django.core.exceptions import ValidationError

from adminfilters.utils import parse_bool
from flags import state as flag_state
from flags.conditions import conditions

if TYPE_CHECKING:
    from typing import Any

    from collections.abc import Iterator

    from django.http import HttpRequest

    from hope_country_report.types.http import AuthHttpRequest


@contextlib.contextmanager
def enable_flag(name: str) -> "Iterator[Any]":
    flag_state.enable_flag(name)
    yield
    flag_state.disable_flag(name)


def validate_bool(value: str) -> None:
    if value.lower() not in ["true", "1", "yes", "t", "y", "false", "0", "no", "f", "n"]:
        raise ValidationError("Enter a valid bool")


@conditions.register("superuser", validator=validate_bool)
def superuser(value: str, request: "AuthHttpRequest|None", **kwargs: "Any") -> bool:
    return request.user.is_superuser == parse_bool(value)


@conditions.register("debug", validator=validate_bool)
def debug(value: str, **kwargs: "Any") -> bool:
    return parse_bool(value) == settings.DEBUG


@conditions.register("Server IP")
def server_ip(value: str, request: "HttpRequest|None", **kwargs: "Any") -> bool:
    return request.META.get("REMOTE_ADDR", "-1") in value.split(",")


@conditions.register("hostname")
def hostname(value: str, request: "HttpRequest|None", **kwargs: "Any") -> bool:
    return request.get_host().split(":")[0] in value.split(",")
