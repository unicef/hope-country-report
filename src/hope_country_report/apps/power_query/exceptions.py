from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from hope_country_report.types.django import AnyModel


class PowerQueryError(Exception):
    pass


class QueryRunError(PowerQueryError):
    def __init__(
        self,
        exception: Exception,
        sentry_error_id: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.exception = exception
        self.sentry_error_id = sentry_error_id

    def __str__(self) -> str:
        return str(f"{self.exception.__class__.__name__}: {self.exception}")


class QueryRunCanceled(PowerQueryError):
    pass


class QueryRunTerminated(PowerQueryError):
    pass


class RequestablePermissionDenied(PowerQueryError):
    def __init__(self, object: "AnyModel") -> None:
        self.object = object
