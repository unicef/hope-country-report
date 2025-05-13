from typing import Callable

from mypy.plugin import ClassDefContext, Plugin
from mypy.plugins.common import add_attribute_to_class

from mypy.types import AnyType, TypeOfAny


def _adjust_request_members(ctx: ClassDefContext) -> None:
    add_attribute_to_class(ctx.api, ctx.cls, "user_agent", AnyType(TypeOfAny.explicit))


class BitcasterMypyPlugin(Plugin):
    def get_base_class_hook(self, fullname: str) -> Callable[[ClassDefContext], None] | None:
        if fullname == "django.http.request.HttpRequest":
            return _adjust_request_members
        return None


def plugin(version: str) -> type[BitcasterMypyPlugin]:
    return BitcasterMypyPlugin
