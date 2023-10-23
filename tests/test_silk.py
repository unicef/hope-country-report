import pytest

from django.conf import settings


def test_SILKY_PYTHON_PROFILER_FUNC(rf):
    try:
        handler = settings.SILKY_PYTHON_PROFILER_FUNC
        handler(rf.get("/"))
    except Exception as e:
        pytest.fail(f"Raised an exception {e}")


def test_SILKY_INTERCEPT_FUNC(rf):
    try:
        handler = settings.SILKY_INTERCEPT_FUNC
        handler(rf.get("/"))
    except Exception as e:
        pytest.fail(f"Raised an exception {e}")
