from typing import Any


def can_slice(maybe_seq: Any) -> bool:
    # Avoid raising an exception (a little faster).
    if (getitem := getattr(maybe_seq, "__getitem__", None)) is None:
        return False
    try:
        getitem(slice(0))
        return True
    except TypeError:
        return False
