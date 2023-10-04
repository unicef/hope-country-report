import re

from django.urls import URLResolver

from hope_country_report.state import state

from .utils import TENANT_PREFiX


class TenantPrefixPattern:
    def __init__(self):
        self.converters = {}

    @property
    def regex(self):
        return re.compile(re.escape(self.tenant_prefix))

        # return re.compile("%s/" % self.tenant_prefix)
        # return re.compile(re.escape(self.language_prefix))

    # @property
    # def language_prefix(self):
    #     # language_code = conf.strategy.get_selected_tenant().pk
    #     return r"t/%s/" % 1
    @property
    def tenant_prefix(self):
        try:
            prefix = state.tenant
            return f"{TENANT_PREFiX}%s/" % (prefix or "")
        except Exception:
            return ""

    def match(self, path):
        tenant_prefix = self.tenant_prefix
        if path.startswith(tenant_prefix):
            return path[len(tenant_prefix) :], (), {}
        return None

    # def match(self, path):
    #     try:
    #         from hope_country_report.apps.core.models import CountryOffice
    #         if g := re.match(self.regex_pattern, path):
    #             prefix = g.group('prefix')
    #             tenant_pk = g.group('tenant')
    #             conf.strategy.set_selected_tenant(CountryOffice.objects.get(code=tenant_pk))
    #             return path[len(prefix)+1:], (), {}
    #         return None
    #     except Exception as e:
    #         logging.exception(e)

    def check(self):
        return []

    def describe(self):
        return "'{}'".format(self)

    def __str__(self):
        return self.tenant_prefix


class TenantURLResolver(URLResolver):
    ...


def tenant_patterns(*urls, namespace=None, app_name=None):
    return [TenantURLResolver(TenantPrefixPattern(), list(urls), namespace=namespace, app_name=app_name)]
