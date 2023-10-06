from typing import Any, TYPE_CHECKING

from django.apps import AppConfig
from django.core.exceptions import ValidationError

from adminfilters.utils import parse_bool

if TYPE_CHECKING:
    from hope_country_report.types.http import AuthHttpRequest


class Config(AppConfig):
    name = __name__.rpartition(".")[0]
    verbose_name = "Core"

    def ready(self) -> None:
        from flags import conditions

        def validate_bool(value: str) -> None:
            if not value.lower() in ["true", "1", "yes", "t", "y", "false", "0", "no", "f", "n"]:
                raise ValidationError("Enter a valid bool")

        @conditions.register("superuser", validator=validate_bool)
        def superuser_condition(value: str, request: "AuthHttpRequest|None" = None, **kwargs: "Any") -> bool:
            return request.user.is_superuser == parse_bool(value)

        @conditions.register("Server IP")
        def server_ip(value: str, request: "AuthHttpRequest|None" = None, **kwargs: "Any") -> bool:
            return request.META.get("REMOTE_ADDR") in value.split(",")

        @conditions.register("hostname")
        def hostname(value: str, request: "AuthHttpRequest|None" = None, **kwargs: "Any") -> bool:
            return request.get_host().split(":")[0] in value.split(",")
