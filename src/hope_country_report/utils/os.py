from typing import Iterator

import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def pushd(path: str | Path) -> Iterator[None]:
    origin = Path().absolute()
    if not path:
        path = origin
    path = Path(path).absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)
