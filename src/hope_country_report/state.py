import json
from threading import local
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, List

    from django.http import HttpResponse

    from hope_country_report.types.http import _R


class State(local):
    request: "_R|None" = None
    tenant: "str|None" = None
    cookies: "dict[str, List[Any]]" = {}

    def __repr__(self) -> str:
        return f"<State {id(self)}>"

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


state = State()
