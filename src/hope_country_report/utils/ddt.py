from typing import TYPE_CHECKING

from django.template import Context, Template
from django.utils.translation import gettext_lazy as _

from debug_toolbar.panels import Panel

from hope_country_report.apps.tenant.config import conf
from hope_country_report.apps.tenant.utils import get_selected_tenant, must_tenant
from hope_country_report.state import state

if TYPE_CHECKING:
    from django.utils.functional import _StrPromise

TEMPLATE = """
<div class="djdt-scroll">
    <h4>Tenant Configuration</h4>
    <table>
        <tbody>
            <tr><th>User</th><td>{{state.request.user}}</td><tr>
            <tr><th>Active</th><td>{{tenant_status}}</td><tr>
            <tr><th>Business Area</th><td>{{active_tenant}}</td><tr>
            <tr><th>Country Office</th><td>{{active_tenant.business_area}}</td><tr>
            <tr><th>Cookie</th><td>{{cookie}}</td><tr>
        </tbody>
    </table>
    <h4>State</h4>
    <table>
        <thead>
            <tr><th>Key</th><th>Value</th><tr>
        </thead>
        <tbody>
            <tr><th>Request</th><td>{{state.request}}</td><tr>
            <tr><th>Tenant</th><td>{{state.tenant}}</td><tr>
            <tr><th>Filters</th><td>{{state.filters}}</td><tr>
        </tbody>
    </table>
    <h4>Tenant Configuration</h4>
    <table>
        <thead>
            <tr><th>Key</th><th>Value</th><tr>
        </thead>
        <tbody>
            <tr><th>COOKIE_NAME</th><td>{{conf.COOKIE_NAME}}</td><tr>
            <tr><th>TENANT_MODEL</th><td>{{conf.TENANT_MODEL}}</td><tr>
            <tr><th>STRATEGY</th><td>{{conf.STRATEGY}}</td><tr>
            <tr><th>AUTH</th><td>{{conf.AUTH}}</td><tr>
        </tbody>
    </table>
    <h4>Permissions</h4>
        <table>
        <tbody>
            <tr><td>{{modules}}</td><tr>
            <tr><td>{{perms}}</td><tr>
        </tbody>
    </table>
</div>
"""


class StateDebugPanel(Panel):
    name: str = "Tenant"
    has_content: bool = True
    panel_id: str = "_state"

    def nav_title(self) -> "_StrPromise":
        return _("Tenant")

    # def nav_subtitle(self):
    #     if is_tenant_active():
    #         return "active"
    #     else:
    #         return "NOT active"

    def title(self) -> "_StrPromise":
        return _("Tenant Debug Panel")

    @property
    def content(self) -> str:
        context = Context({})
        context.update(
            {
                "state": state,
                "conf": conf,
                "active_tenant": get_selected_tenant(),
                "tenant_status": must_tenant(),
                # "cookie": get_tenant_from_request(state.request),
                # "perms": state.request.user.get_all_permissions(),
                # "modules": conf.auth.get_available_modules(state.request.user),
            }
        )
        tpl = Template(TEMPLATE)
        return tpl.render(context)
