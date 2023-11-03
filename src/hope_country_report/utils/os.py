import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def pushd(path: str | Path) -> None:
    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)
