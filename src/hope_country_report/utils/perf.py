import contextlib
import resource
import time
from typing import Iterator, TYPE_CHECKING

from django.conf import settings
from django.db import connections

if TYPE_CHECKING:
    from typing import Any


class DBMetrics:
    def __init__(self) -> None:
        self.count = 0
        self.elapsed_query_time = 0.0

    def __call__(self, execute: "Any", sql: "Any", params: "Any", many: "Any", context: "Any") -> "Any":
        start_time = time.time()
        try:
            return execute(sql, params, many, context)
        finally:
            self.count += 1
            self.elapsed_query_time += time.time() - start_time


@contextlib.contextmanager
def profile_db() -> "Any":
    metrics = DBMetrics()
    yield connections[settings.POWER_QUERY_DB_ALIAS].execute_wrapper(metrics)


@contextlib.contextmanager
def profile() -> "Iterator[Any]":
    time_start = time.perf_counter()
    mem_start = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0
    info = {"time_start": time_start}
    yield info
    time_end = time.perf_counter()
    time_elapsed = time_end - time_start
    mem_end = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0
    info["time_end"] = time_end
    info["time_elapsed"] = time_elapsed
    info["memory"] = mem_end - mem_start
