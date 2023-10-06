import contextlib
import json
from typing import Dict, TYPE_CHECKING

from hope_country_report.utils.singleton import Singleton

if TYPE_CHECKING:
    from typing import Any, List

    from django.http import HttpResponse

    from hope_country_report.types.http import _R

not_set = object()


# class State(local):
class State(metaclass=Singleton):
    request: "_R|None" = None
    tenant: "str|None" = None
    cookies: "dict[str, List[Any]]" = {}
    filters: "List[str]" = []

    def __repr__(self) -> str:
        return f"<State {id(self)}>"

    @contextlib.contextmanager
    def set(self, **kwargs: "Dict[str,Any]") -> None:
        pre = {}
        for k, v in kwargs.items():
            if hasattr(self, k):
                pre[k] = getattr(self, k)
            else:
                pre[k] = not_set
            setattr(self, k, v)
        yield
        for k, v in pre.items():
            if v is not_set:
                delattr(self, k)
            else:
                setattr(self, k, v)

    def add_cookies(
        self,
        key: str,
        value: str,
        max_age: "int|None" = None,
        expires: "int|None" = None,
        path: str = "/",
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: "Any" = None,
    ) -> None:
        value = json.dumps(value)
        self.cookies[key] = [value, max_age, expires, path, domain, secure, httponly, samesite]

    def set_cookies(self, response: "HttpResponse") -> None:
        for name, args in self.cookies.items():
            response.set_cookie(name, *args)

    def reset(self) -> None:
        self.tenant = None
        self.request = None
        self.cookies = {}
        self.filters = []


state = State()
