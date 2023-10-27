from typing import Any, Optional, Type, TYPE_CHECKING

import logging
from collections.abc import Sequence

from unittest.mock import Mock

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse

import tablib
from admin_extra_buttons.decorators import button, view
from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminactions.helpers import AdminActionPermMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from constance import config
from django_celery_results.models import TaskResult
from import_export import resources
from smart_admin.mixins import DisplayAllMixin, LinkedObjectsMixin

from ...state import state
from ...utils.perf import profile
from .forms import FormatterTestForm, QueryForm, SelectDatasetForm
from .models import CeleryEnabled, Dataset, Formatter, Parametrizer, Query, Report, ReportDocument, ReportTemplate
from .processors import ProcessorStrategy, registry
from .utils import to_dataset
from .widget import FormatterEditor

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from django.contrib.admin.options import _ListFilterT, _ModelT

    from ...types.django import AnyModel


class CeleryEnabledMixin(admin.ModelAdmin):
    def get_readonly_fields(self, request: HttpRequest, obj: Optional["AnyModel"] = None) -> Sequence[str]:
        ret = list(super().get_readonly_fields(request, obj))
        ret.append("curr_async_result_id")
        return ret

    @button()
    def check_status(self, request: HttpRequest) -> "HttpResponse":
        obj: CeleryEnabled
        for obj in self.get_queryset(request):
            if obj.async_result is None:
                obj.curr_async_result_id = None
                obj.save()

    @view()
    def celery_discard_all(self, request: HttpRequest) -> "HttpResponse":
        self.model.discard_all()

    @view()
    def celery_purge(self, request: HttpRequest) -> "HttpResponse":
        self.model.purge()

    @view()
    def celery_terminate(self, request: HttpRequest, pk: int) -> "HttpResponse":
        obj: CeleryEnabled = self.get_object(request, pk)
        obj.terminate()

    @view()
    def celery_inspect(self, request: HttpRequest, pk: int) -> HttpResponse:
        ctx = self.get_common_context(request, pk=pk)
        return render(
            request,
            f"admin/power_query/{self.model._meta.model_name}/inspect.html",
            ctx,
        )

    @view()
    def celery_result(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.get_common_context(request, pk=pk)
        result = TaskResult.objects.filter(task_id=self.object.curr_async_result_id).first()
        if result:
            url = reverse("admin:django_celery_results_taskresult_change", args=[result.pk])
            return redirect(url)
        else:
            self.message_user(request, "Result not found", messages.ERROR)

    @view()
    def celery_queue(self, request: "HttpRequest", pk: int) -> "HttpResponse":
        obj: CeleryEnabled | None
        try:
            obj = self.get_object(request, str(pk))
            if obj.queue():
                self.message_user(request, f"Task scheduled: {obj.curr_async_result_id}")
        except Exception as e:
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)

    @property
    def media(self):
        response = super().media
        response._js_lists.append(["admin/celery.js"])
        return response


class AutoProjectCol(admin.ModelAdmin):
    def get_list_display(self, request: "HttpRequest") -> Sequence[str]:
        base = super().get_list_display(request)
        if state.tenant is None:
            return ("country_office", *base)
        return base

    def get_list_filter(self, request: "HttpRequest") -> "Sequence[_ListFilterT]":
        base = super().get_list_filter(request)
        return (("country_office", AutoCompleteFilter), *base)

    def get_autocomplete_fields(self, request: HttpRequest) -> Sequence[str]:
        base = super().get_autocomplete_fields(request)
        return ("country_office", *base)


@admin.register(Query)
class QueryAdmin(
    AdminFiltersMixin,
    AutoProjectCol,
    CeleryEnabledMixin,
    ExtraButtonsMixin,
    DisplayAllMixin,
    AdminActionPermMixin,
    ModelAdmin,
):
    list_display = ("name", "target", "owner", "active", "success", "last_run", "status")
    search_fields = ("name",)
    list_filter = (
        ("target", AutoCompleteFilter),
        ("owner", AutoCompleteFilter),
        "active",
        "last_run",
    )
    linked_objects_template = None
    autocomplete_fields = ("target", "owner")
    readonly_fields = ("sentry_error_id", "error_message", "info")
    change_form_template = None
    ordering = ["-last_run"]
    form = QueryForm

    def get_queryset(self, request: HttpRequest) -> "QuerySet[AnyModel]":
        return super().get_queryset(request).select_related("target", "owner")

    def success(self, obj: Query) -> bool:
        return not bool(obj.error_message)

    success.boolean = True

    def change_view(
        self, request: "HttpRequest", object_id: str, form_url: str = "", extra_context: "dict[str, Any] | None" = None
    ) -> "HttpResponse":
        return super().change_view(request, object_id, form_url, extra_context)

    # def get_form(
    #     self, request: "HttpRequest", obj: "_ModelT|None" = None, change: bool = False, **kwargs: Any
    # ) -> "type[ModelForm[_ModelT]]":
    #     # kwargs["initial"] = {"project": get_selected_tenant()}
    #     return super().get_form(request, obj, change, **kwargs)
    #
    # def formfield_for_dbfield(self,
    # db_field: Any, request: HttpRequest, **kwargs: Any) -> Optional[forms.fields.Field]:
    #     if db_field.name == "code":
    #         kwargs = {"widget": PythonFormatterEditor}
    #     elif db_field.name == "description":
    #         kwargs = {"widget": forms.Textarea(attrs={"rows": 2, "style": "width:80%"})}
    #     elif db_field.name == "project":
    #         from hope_country_report.apps.tenant.config import conf
    #
    #         db_field.queryset = conf.auth.get_allowed_tenants()
    #     elif db_field.name == "owner":
    #         kwargs = {"widget": forms.HiddenInput}
    #
    #     return super().formfield_for_dbfield(db_field, request, **kwargs)

    def has_change_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return super().has_change_permission(request, obj)
        # if isinstance(obj, int):
        # return request.user.is_superuser or bool(obj and obj.owner == request.user)

    @button()
    def datasets(self, request: HttpRequest, pk: int) -> HttpResponseRedirect:
        obj = self.get_object(request, str(pk))
        try:
            url = reverse("admin:power_query_dataset_changelist")
            return HttpResponseRedirect(f"{url}?query__exact={obj.pk}")
        except Exception as e:  # pragma: no cover
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)

    @button(visible=settings.DEBUG)
    def run(self, request: HttpRequest, pk: int) -> HttpResponse:
        ctx = self.get_common_context(request, pk, title="Run results")
        query = self.get_object(request, str(pk))
        results = query.execute_matrix(persist=True)
        self.message_user(request, "Done", messages.SUCCESS)
        ctx["results"] = results
        return render(request, "admin/power_query/query/run_result.html", ctx)

    # @button()
    # def queue(self, request: HttpRequest, pk: int) -> HttpResponseRedirect:  # type: ignore[return]
    #     try:
    #         res: AsyncResult = run_background_query.delay(pk)
    #         self.message_user(request, f"Query scheduled: {res}")
    #     except Exception as e:
    #         self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)

    @button()
    def preview(self, request: HttpRequest, pk: int) -> HttpResponse:
        obj: Query = self.get_object(request, str(pk))
        try:
            context = self.get_common_context(request, pk, title="Results")
            if obj.parametrizer:
                args = obj.parametrizer.get_matrix()[0]
            else:
                args = {}
            with profile() as timing:
                ds, extra = obj.run(False, args, use_existing=True, preview=True)
            ret = ds.data

            context["type"] = type(ret).__name__
            context["raw"] = ret
            context["info"] = extra
            context["title"] = f"Result of {obj.name} ({type(ret).__name__})"
            context["timing"] = timing
            if isinstance(ret, QuerySet):
                ret = ret[: config.PQ_SAMPLE_PAGE_SIZE]
                context["queryset"] = ret
            elif isinstance(ret, tablib.Dataset):
                context["dataset"] = ret[: config.PQ_SAMPLE_PAGE_SIZE]
            elif isinstance(ret, (dict, list, tuple)):
                context["result"] = ret[: config.PQ_SAMPLE_PAGE_SIZE]
            else:
                self.message_user(
                    request, f"Query does not returns a valid result. It returned {type(ret)}", messages.WARNING
                )
            return render(request, "admin/power_query/query/preview.html", context)
        except Exception as e:
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        ct = ContentType.objects.filter(id=request.GET.get("ct", 0)).first()
        return {
            "code": "result=conn.all()",
            "name": ct,
            "target": ct,
            "owner": request.user,
        }


class FileProviderAdmin(admin.ModelAdmin):
    actions = ["check_files"]

    def delete_model(self, request: "HttpRequest", obj: "_ModelT") -> None:
        super().delete_model(request, obj)

    def check_files(self, request: HttpRequest, queryset) -> HttpResponse:
        for m in queryset.all():
            try:
                if not m.file.exists():
                    m.file = None
                    m.save()
            except Exception:
                pass

    @button()
    def _check_files(self, request: HttpRequest) -> HttpResponse:
        return self.check_files(request, self.model.objects.all())


@admin.register(Dataset)
class DatasetAdmin(
    AdminFiltersMixin,
    ExtraButtonsMixin,
    DisplayAllMixin,
    AdminActionPermMixin,
    FileProviderAdmin,
    ModelAdmin,
):
    search_fields = ("query__name",)
    list_display = (
        "query",
        "last_run",
        "dataset_type",
        "target_type",
        "size",
        "arguments",
    )
    list_filter = (
        ("query__target", AutoCompleteFilter),
        ("query", AutoCompleteFilter),
        "last_run",
    )
    change_form_template = None
    readonly_fields = ("last_run", "query", "info")
    date_hierarchy = "last_run"

    def get_queryset(self, request: HttpRequest):  # type: ignore[no-untyped-def]
        return super().get_queryset(request).select_related("query", "query__target").defer("extra")

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def arguments(self, obj: Any) -> str:
        return obj.info.get("arguments")

    def dataset_type(self, obj: Any) -> str:
        return obj.info.get("type")

    def target_type(self, obj: Any) -> str:
        return obj.query.target

    @button(visible=lambda btn: "change" in btn.context["request"].path)
    def analyze(self, request: HttpRequest, pk: int) -> HttpResponse:
        context = self.get_common_context(request, pk, title="Results")
        return render(request, "admin/power_query/query/analyze.html", context)

    @button(visible=lambda btn: "change" in btn.context["request"].path)
    def preview(self, request: HttpRequest, pk: int) -> HttpResponse:
        obj = self.get_object(request, str(pk))
        try:
            context = self.get_common_context(request, pk, title="Results")
            data = obj.data
            with profile() as timing:
                context["dataset"] = to_dataset(data)
            context["timing"] = timing
            return render(request, "admin/power_query/query/preview.html", context)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)


class FormatterResource(resources.ModelResource):
    class Meta:
        model = Report
        fields = ("name", "content_type", "code")
        import_id_fields = ("name",)


@admin.register(Formatter)
class FormatterAdmin(
    ExtraButtonsMixin,
    DisplayAllMixin,
    AdminActionPermMixin,
    ModelAdmin,
):
    list_display = ("name", "strategy", "content_type")
    search_fields = ("name",)
    list_filter = ("processor",)
    resource_class = FormatterResource
    change_form_template = None

    formfield_overrides = {
        models.TextField: {"widget": FormatterEditor(theme="abcdef")},
    }

    def strategy(self, obj: Formatter) -> str:
        return obj.processor.label

    @button(visible=lambda btn: "change" in btn.context["request"].path)
    def test(self, request: HttpRequest, pk: int) -> HttpResponse:
        context = self.get_common_context(request, pk)
        form = FormatterTestForm()
        try:
            if request.method == "POST":
                form = FormatterTestForm(request.POST)
                if form.is_valid():
                    obj: Formatter = self.object
                    ctx = {
                        "dataset": form.cleaned_data["query"].datasets.first(),
                        "report": "None",
                    }
                    if obj.content_type == ".xls":
                        output = obj.render(ctx)
                        response = HttpResponse(output, content_type=obj.content_type)
                        response["Content-Disposition"] = "attachment; filename=Report.xls"
                        return response
                    else:
                        context["results"] = obj.render(ctx).decode()
        except Exception as e:
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)
        context["form"] = form
        return render(request, "admin/power_query/formatter/test.html", context)


@admin.register(ReportTemplate)
class ReportTemplateAdmin(AdminFiltersMixin, ExtraButtonsMixin, AdminActionPermMixin, ModelAdmin):
    list_display = (
        "name",
        "doc",
        "file_suffix",
    )
    search_fields = ("name",)
    list_filter = ("file_suffix",)
    autocomplete_fields = ("country_office",)

    # readonly_fields = ("suffix", )

    @button()
    def preview(self, request: "HttpRequest", pk: int) -> HttpResponse:
        context = self.get_common_context(request, pk)
        if request.method == "POST":
            form = SelectDatasetForm(request.POST)
            form.fields["processor"].choices = registry.as_choices(lambda x: x.content_type == self.object.content_type)
            if form.is_valid():
                processor: "Type[ProcessorStrategy]" = form.cleaned_data["processor"]
                fmt = Mock()
                fmt.doc = self.object
                content = processor(fmt).process({"dataset": form.cleaned_data["dataset"]})
                return HttpResponse(content, content_type=processor.content_type)
        else:
            context["form"] = SelectDatasetForm()
        return render(request, "admin/power_query/reporttemplate/preview.html", context)


@admin.register(Report)
class ReportAdmin(
    AdminFiltersMixin,
    CeleryEnabledMixin,
    LinkedObjectsMixin,
    ExtraButtonsMixin,
    DisplayAllMixin,
    AdminActionPermMixin,
    ModelAdmin,
):
    list_display = ("country_office", "name", "formatters", "last_run", "owner", "schedule")
    autocomplete_fields = ("query", "owner")
    filter_horizontal = ["limit_access_to", "formatters"]
    readonly_fields = (
        "last_run",
        "sentry_error_id",
        "error_message",
        "last_async_result_id",
    )
    list_filter = (
        ("country_office", AutoCompleteFilter),
        ("owner", AutoCompleteFilter),
        ("query", AutoCompleteFilter),
        ("formatters", AutoCompleteFilter),
        "last_run",
    )
    search_fields = ("name",)
    change_form_template = None
    linked_objects_hide_empty = False
    object: "Report"

    def has_change_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return request.user.is_superuser or bool(obj and obj.owner == request.user)

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"owner": request.user}
        if "q" in request.GET:
            q = Query.objects.get(pk=request.GET["q"])
            kwargs["query"] = q
            kwargs["name"] = f"Report for {q.name}"
            kwargs["notify_to"] = [request.user]
        return kwargs

    @button(visible=lambda btn: "change" in btn.context["request"].path)
    def execute(self, request: HttpRequest, pk: int) -> HttpResponse:
        ctx = self.get_common_context(request, pk, title="Execution results")
        try:
            results = self.object.execute(run_query=True)
            errors = [r[1] for r in results if isinstance(r[1], Exception)]
            if len(errors) == 0:
                self.message_user(request, "Documents creation success", messages.SUCCESS)
            elif len(errors) == len(results):
                self.message_user(request, "All documents failed", messages.ERROR)
            else:
                self.message_user(request, "Documents created with errors", messages.WARNING)
            ctx["results"] = results
            return render(request, "admin/power_query/report/exec.html", ctx)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)


@admin.register(Parametrizer)
class QueryArgsAdmin(
    AdminFiltersMixin,
    AutoProjectCol,
    LinkedObjectsMixin,
    ExtraButtonsMixin,
    DisplayAllMixin,
    AdminActionPermMixin,
    ModelAdmin,
):
    list_display = ("name", "code", "system")
    list_filter = ("system",)
    search_fields = ("name", "code")
    json_enabled = True

    @button()
    def preview(self, request: HttpRequest, pk: int) -> TemplateResponse:
        context = self.get_common_context(request, pk, title="Execution Plan")
        return TemplateResponse(request, "admin/power_query/queryargs/preview.html", context)

    @button()
    def refresh(self, request: HttpRequest, pk: int) -> None:
        obj = self.get_object(request, str(pk))
        obj.refresh()


@admin.register(ReportDocument)
class ReportDocumentAdmin(
    AdminFiltersMixin,
    LinkedObjectsMixin,
    FileProviderAdmin,
    ExtraButtonsMixin,
    DisplayAllMixin,
    AdminActionPermMixin,
    ModelAdmin,
):
    list_display = ("title", "content_type", "report", "file")
    list_filter = (("report", AutoCompleteFilter),)
    search_fields = ("title",)
    filter_horizontal = ("limit_access_to",)
    readonly_fields = ("arguments", "report", "dataset", "content_type")

    def get_queryset(self, request: HttpRequest) -> QuerySet[ReportDocument]:
        return super().get_queryset(request)

    # def size(self, obj: ReportDocument) -> int:
    #     return len(obj.output or "")
    #
    # @button()
    # def view(self, request: HttpRequest, pk: int) -> HttpResponseRedirect:
    #     if not (obj := self.get_object(request, str(pk))):
    #         raise Exception("Report document not found")
    #     url = reverse("power_query:document", args=[obj.report.pk, pk])
    #     return HttpResponseRedirect(url)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
