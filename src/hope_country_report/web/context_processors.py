import json
import os
from typing import TYPE_CHECKING

from django.conf import settings

from hope_country_report.apps.tenant.utils import get_selected_tenant
from hope_country_report.state import state as global_state

if TYPE_CHECKING:
    from typing import Any

    from hope_country_report.types.http import AuthHttpRequest


_project_info = {}
try:
    with open("/RELEASE", encoding="utf-8") as f:
        _project_info = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    pass


def state(request: "AuthHttpRequest") -> "dict[str, Any]":
    return {
        "state": global_state,
        "selected_tenant": get_selected_tenant(),
        "tenant_cookie": global_state.tenant_cookie,
        "project": {
            "build_date": _project_info.get("date", os.environ.get("BUILD_DATE", "no date")),
            "version": _project_info.get("version", os.environ.get("VERSION", "dev")),
            "commit": _project_info.get("commit", os.environ.get("SOURCE_COMMIT", "<dev>")),
            "debug": settings.DEBUG,
        },
    }
