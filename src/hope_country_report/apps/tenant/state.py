import threading
from functools import cached_property, lru_cache

VERSION = __version__ = "0.1.0"

_locals = threading.local()


def get_current_request():
    return getattr(_locals, "request", None)


@lru_cache(None)
class State:
    @cached_property
    def tenant(self):
        return


state = State()
