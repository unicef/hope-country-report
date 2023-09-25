# from hope_country_report.apps.core.models import CountryOffice
# from power_query.admin import CeleryEnabledMixin
# from power_query.models import Formatter, Parametrizer, Query, Report, ReportDocument
# from tenant_admin.config import conf
# from tenant_admin.options import TenantModelAdmin
#
#
# class QueryAdmin(CeleryEnabledMixin, TenantModelAdmin):
#     model = Query
#     tenant_filter_field = "project"
#     list_display = ("project", "name", "target", "active")
#     # search_fields = ("full_name",)
#     # list_filter = (("household__unicef_id", ValueFilter), "relationship")
#     autocomplete_fields = ("project",)
#
#     def save_form(self, request, form, change):
#         form.instance.project = CountryOffice.objects.get(id=conf.strategy.get_selected_tenant(request).id)
#         return form.save(commit=False)
#
#     def has_change_permission(self, request, obj=None):
#         return True
#
#
# class ParametrizerAdmin(TenantModelAdmin):
#     model = Parametrizer
#     tenant_filter_field = "__none__"
#     # search_fields = ("full_name",)
#     # list_filter = (("household__unicef_id", ValueFilter), "relationship")
#
#
# class ReportDocumentAdmin(TenantModelAdmin):
#     model = ReportDocument
#     tenant_filter_field = "__none__"
#     # search_fields = ("full_name",)
#     # list_filter = (("household__unicef_id", ValueFilter), "relationship")
#
#
# class ReportAdmin(TenantModelAdmin):
#     model = Report
#     tenant_filter_field = "__none__"
#     # search_fields = ("full_name",)
#     # list_filter = (("household__unicef_id", ValueFilter), "relationship")
#
#
# class FormatterAdmin(TenantModelAdmin):
#     model = Formatter
#     tenant_filter_field = "__none__"
#     # search_fields = ("full_name",)
#     # list_filter = (("household__unicef_id", ValueFilter), "relationship")
