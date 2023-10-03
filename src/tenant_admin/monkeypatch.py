import django.contrib.admin.helpers
from django.contrib.admin.utils import quote
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html

from hope_country_report.state import state
from tenant_admin.config import conf


class TenantAdminReadonlyField(django.contrib.admin.helpers.AdminReadonlyField):
    def get_admin_url(self, remote_field, remote_obj):
        if state.request.path.startswith("/t/"):
            namespace = conf.NAMESPACE
        else:
            namespace = "admin"
        url_name = "%s:%s_%s_change" % (
            namespace,
            remote_field.model._meta.app_label,
            remote_field.model._meta.model_name,
        )
        try:
            url = reverse(
                url_name,
                args=[quote(remote_obj.pk)],
                current_app=self.model_admin.admin_site.name,
            )
            return format_html('<a href="{}">{}</a>', url, remote_obj)
        except NoReverseMatch:
            return str(remote_obj)


django.contrib.admin.helpers.AdminReadonlyField = TenantAdminReadonlyField
