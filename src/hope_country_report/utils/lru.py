from typing import TYPE_CHECKING

from functools import lru_cache, wraps

if TYPE_CHECKING:
    from typing import Any, Callable


def lru_cache_not_none(maxsize: int = 128, typed: bool = False) -> "Callable[Any]":
    class ValueIsNone(Exception):
        pass

    def decorator(func: "Callable[Any]") -> "Callable[Any]":
        @lru_cache(maxsize=maxsize, typed=typed)
        def raise_exception_wrapper(*args: "Any", **kwargs: "Any") -> "Any":
            value = func(*args, **kwargs)
            if value is None:
                raise ValueIsNone
            return value

        @wraps(func)
        def handle_exception_wrapper(*args: "Any", **kwargs: "Any") -> "Any":
            try:
                return raise_exception_wrapper(*args, **kwargs)
            except ValueIsNone:
                return None

        handle_exception_wrapper.cache_info = raise_exception_wrapper.cache_info
        handle_exception_wrapper.cache_clear = raise_exception_wrapper.cache_clear
        return handle_exception_wrapper

    if callable(maxsize):
        user_function, maxsize = maxsize, 128
        return decorator(user_function)

    return decorator
