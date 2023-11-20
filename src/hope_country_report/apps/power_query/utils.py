from typing import Any, Dict, TYPE_CHECKING

import base64
import binascii
import hashlib
import json
import logging
from collections.abc import Callable, Iterable
from functools import wraps
from pathlib import Path

from django.conf import settings
from django.contrib.auth import authenticate
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils.safestring import mark_safe

import tablib
from constance import config
from sentry_sdk import configure_scope

if TYPE_CHECKING:
    from hope_country_report.types.django import AnyModel


logger = logging.getLogger(__name__)


def is_valid_template(filename: Path) -> bool:
    if filename.suffix not in [".docx", ".pdf"]:
        return False
    if filename.stem.startswith("~"):
        return False
    if filename.stem.startswith("."):
        return False
    return True


def to_dataset(result: "QuerySet[AnyModel]|Iterable[Any]|tablib.Dataset|Dict[str,Any]") -> tablib.Dataset:
    if isinstance(result, QuerySet):
        data = tablib.Dataset()
        fields = result.__dict__["_fields"]
        if not fields:
            fields = [field.name for field in result.model._meta.concrete_fields]
        data.headers = fields
        try:
            for obj in result.using(settings.POWER_QUERY_DB_ALIAS).all()[: config.PQ_SAMPLE_PAGE_SIZE]:
                line = []
                for f in fields:
                    # if isinstance(obj, dict):
                    #     line.append(obj[f])
                    if isinstance(obj, tuple):
                        line.append(str(obj))
                    else:
                        line.append(str(getattr(obj, f)))
                data.append(line)
                # data.append([obj[f] if isinstance(obj, dict) else str(getattr(obj, f)) for f in fields])
        except Exception as e:
            logger.exception(e)
            raise
            # raise ValueError(f"Results can't be rendered as a tablib Dataset: {e}")
    elif isinstance(result, (list, tuple)):
        data = tablib.Dataset()
        fields = set().union(*(d.keys() for d in list(result)))
        data.headers = fields
        try:
            for obj in result:
                data.append([obj[f] for f in fields])
        except Exception:
            raise ValueError("Results can't be rendered as a tablib Dataset")
    elif isinstance(result, (tablib.Dataset, dict)):
        data = result
    else:
        raise ValueError(f"{result} ({type(result)}")
    return data


def get_sentry_url(event_id: int, html: bool = False) -> str:
    url = f"{settings.SENTRY_URL}?query={event_id}"
    if html:
        return mark_safe('<a href="{url}" target="_sentry" >View on Sentry<a/>')
    return url


def basicauth(view: Callable[..., Callable]) -> Callable[..., Any]:
    def wrap(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return view(request, *args, **kwargs)

        if "HTTP_AUTHORIZATION" in request.META:
            try:
                auth = request.headers["Authorization"].split()
                if len(auth) == 2:
                    if auth[0].lower() == "basic":
                        uname, passwd = base64.b64decode(auth[1].encode()).decode().split(":")
                        user = authenticate(username=uname, password=passwd)
                        if user is not None and user.is_active:
                            request.user = user
                            return view(request, *args, **kwargs)
            except binascii.Error:
                pass
        response = HttpResponse()
        response.status_code = 401
        response["WWW-Authenticate"] = 'Basic realm="HOPE"'
        return response

    return wrap


def sizeof(num: float, suffix: str = "") -> str:
    for unit in ["b", "Kb", "Mb", "Gb", "Tb", "Pb", "Eb", "Zb"]:
        if num % 1 == 0:
            n = f"{abs(num):.0f}"
        else:
            n = f"{num:3.1f}"
        if abs(num) < 1024.0:
            return f"{n} {unit}{suffix}".strip()
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}".strip()


def dict_hash(dictionary: dict[str, Any]) -> str:
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is
    # the same as {'b': 2, 'a': 1}
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()


def sentry_tags(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        with configure_scope() as scope:
            scope.set_tag("celery", True)
            scope.set_tag("celery_task", func.__name__)

            return func(*args, **kwargs)

    return wrapper
