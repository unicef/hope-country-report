from typing import Any, Dict, Tuple


class Singleton(type, metaclass=object):
    def __init__(cls, name: str, bases: "Tuple[type]", d: "Dict[Any,Any]"):
        super().__init__(name, bases, d)
        cls.instance = None

    def __call__(cls, *args: "Any", **kwds: "Any") -> "Any":
        if cls.instance is None:
            cls.instance = super().__call__(*args)
        return cls.instance
