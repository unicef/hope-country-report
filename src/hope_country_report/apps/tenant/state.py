import threading
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice
    from hope_country_report.types.http import _R

VERSION = __version__ = "0.1.0"

_locals = threading.local()


def get_current_request() -> "_R":
    return getattr(_locals, "request", None)


@lru_cache(None)
class State:
    tenant: "CountryOffice"


state = State()
