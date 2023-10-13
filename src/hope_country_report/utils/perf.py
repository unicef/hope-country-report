from typing import Iterator, TYPE_CHECKING

import contextlib
import resource
import time

from django.conf import settings
from django.db import connections

if TYPE_CHECKING:
    from typing import Any, Dict


class DBMetrics:
    def __init__(self, conn: str) -> None:
        self.conn = conn
        self.count = 0
        self.elapsed_query_time = 0.0
        self.clauses = []

    def __call__(self, execute: "Any", sql: "Any", params: "Any", many: "Any", context: "Any") -> "Any":
        start_time = time.time()
        try:
            return execute(sql, params, many, context)
        finally:
            self.clauses.append([sql, params])
            self.count += 1
            self.elapsed_query_time += time.time() - start_time


@contextlib.contextmanager
def profile() -> "Iterator[Any]":
    time_start = time.perf_counter()
    mem_start = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0
    info: "Dict[str,Any]" = {"time_start": time_start}
    metrics1 = DBMetrics("default")
    metrics2 = DBMetrics(settings.POWER_QUERY_DB_ALIAS)
    with connections["default"].execute_wrapper(metrics1):
        with connections[settings.POWER_QUERY_DB_ALIAS].execute_wrapper(metrics2):
            yield info
    time_end = time.perf_counter()
    time_elapsed = time_end - time_start
    mem_end = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0
    info["time_end"] = time_end
    info["time_elapsed"] = time_elapsed
    info["memory"] = mem_end - mem_start
    info["db"] = {
        "default": {
            "count": metrics1.count,
            "queries": metrics1.clauses,
        },
        settings.POWER_QUERY_DB_ALIAS: {
            "count": metrics2.count,
            "queries": metrics2.clauses,
        },
    }
