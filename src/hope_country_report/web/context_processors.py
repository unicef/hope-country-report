from typing import TYPE_CHECKING

from hope_country_report.apps.tenant.utils import get_selected_tenant
from hope_country_report.state import state as global_state

if TYPE_CHECKING:
    from typing import Any

    from hope_country_report.types.http import AuthHttpRequest


def state(request: "AuthHttpRequest") -> "dict[str, Any]":
    return {
        "state": global_state,
        "selected_tenant": get_selected_tenant(),
        "tenant_cookie": global_state.tenant_cookie,
    }
