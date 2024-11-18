from typing import Callable, List, Tuple, TYPE_CHECKING

import logging
from collections.abc import Sequence

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.db import connections, models
from django.db.models import QuerySet
from django.forms import Media
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.module_loading import import_string

import tablib
from admin_extra_buttons.decorators import button, view
from admin_extra_buttons.mixins import ExtraButtonsMixin
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer
from adminactions.helpers import AdminActionPermMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from constance import config
from debug_toolbar.panels.sql.utils import reformat_sql
from django_celery_results.models import TaskResult
from smart_admin.mixins import DisplayAllMixin, LinkedObjectsMixin

from ...state import state
from ...utils.mail import send_document_password
from ...utils.media import download_media
from ...utils.perf import profile
from .forms import ExplainQueryForm, FormatterTestForm, QueryForm, SelectDatasetForm
from .models import (
    CeleryEnabled,
    ChartPage,
    Dataset,
    Formatter,
    Parametrizer,
    Query,
    ReportConfiguration,
    ReportDocument,
    ReportTemplate,
)
from .models._base import FileProviderMixin
from .utils import to_dataset
from .widget import FormatterEditor

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Type

    from django.contrib.admin.options import _ListFilterT

    from ...types.django import AnyModel
    from ...types.http import AuthHttpRequest
    from .processors import ProcessorStrategy

    _ListDisplayT = List[str | Callable[[Any], str | bool]] | Tuple[str | Callable[[Any], str | bool],] | tuple[()]


class CeleryEnabledMixin(admin.ModelAdmin):
    def get_readonly_fields(self, request: HttpRequest, obj: "Optional[AnyModel]" = None) -> Sequence[str]:
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
    def celery_terminate(self, request: HttpRequest, pk: str) -> "HttpResponse":
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
    def media(self) -> Media:
        response = super().media
        response._js_lists.append(["admin/celery.js"])
        return response


class AutoProjectCol(admin.ModelAdmin):
    def get_list_display(self, request: "HttpRequest") -> "_ListDisplayT":
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
    ModelAdmin[Query],
):
    list_display = ("name", "parent", "target", "owner", "active", "success", "last_run", "status")
    search_fields = ("name",)
    list_filter = (
        ("target", AutoCompleteFilter),
        ("owner", AutoCompleteFilter),
        "active",
        "last_run",
    )
    linked_objects_template = None
    autocomplete_fields = ("target", "owner", "target")
    readonly_fields = (
        "sentry_error_id",
        "error_message",
        "info",
        "last_run",
        "last_async_result_id",
        "curr_async_result_id",
    )
    change_form_template = None
    ordering = ["-last_run"]
    form = QueryForm
    date_hierarchy = "datasets__last_run"

    def get_queryset(self, request: HttpRequest) -> "QuerySet[AnyModel]":
        return super().get_queryset(request).select_related("target", "owner")

    def success(self, obj: Query) -> bool:
        return not bool(obj.error_message)

    success.boolean = True

    def change_view(
        self, request: "HttpRequest", object_id: str, form_url: str = "", extra_context: "dict[str, Any] | None" = None
    ) -> "HttpResponse":
        return super().change_view(request, object_id, form_url, extra_context)

    def has_change_permission(self, request: HttpRequest, obj: "Any|None" = None) -> bool:
        return super().has_change_permission(request, obj)

    @button()
    def explain(self, request: HttpRequest, pk: int) -> HttpResponse:
        context = self.get_common_context(request, pk)
        if request.method == "POST":
            form = ExplainQueryForm(request.POST)
            if form.is_valid():
                q = form.cleaned_data["query"]
                ct: ContentType = form.cleaned_data["target"]
                code = f"""sql={q}.query"""
                locals_ = {"conn": ct.model_class().objects}
                exec(code, globals(), locals_)
                sql = locals_.get("sql", None)
                if sql:
                    cursor = connections[settings.POWER_QUERY_DB_ALIAS].cursor()
                    context["sql"] = reformat_sql(str(locals_.get("sql", "")))
                    cursor.execute(f"EXPLAIN ANALYZE {sql}")
                    headers = [d[0] for d in cursor.description]
                    result = cursor.fetchall()
                    context.update(
                        **{
                            "result": result,
                            "sql": sql,
                            "headers": headers,
                            "alias": settings.POWER_QUERY_DB_ALIAS,
                        }
                    )
                self.message_user(request, code)
                # context["explain_info"] = json.loads(explain_info)
        else:
            form = ExplainQueryForm(initial={"query": "conn.all()", "target": None})

        context["form"] = form
        return render(request, "admin/power_query/query/explain.html", context)

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

    @button()
    def preview(self, request: HttpRequest, pk: int) -> HttpResponse | HttpResponseRedirect:
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
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)
        return HttpResponseRedirectToReferrer(request)

    @button()
    def see_children(self, request: HttpRequest, pk: int) -> "HttpResponse":
        url = reverse("admin:power_query_query_changelist")
        return redirect(f"{url}?parent__id={pk}")

    def get_changeform_initial_data(self, request: HttpRequest) -> "Dict[str, Any]":
        ct = ContentType.objects.filter(id=request.GET.get("ct", 0)).first()
        return {"code": "result=conn.all()", "name": ct, "target": ct, "owner": request.user}


class FileProviderAdmin(admin.ModelAdmin):
    actions = ["check_files"]

    def check_files(self, request: "HttpRequest", queryset: "QuerySet[Any, Any]") -> None:
        m: FileProviderMixin
        for m in queryset.all():
            try:
                if m.file and not m.file.exists():
                    m.file = None
                    m.save()
            except Exception:
                pass

    @button()
    def _check_files(self, request: HttpRequest) -> HttpResponse:
        self.check_files(request, self.model.objects.all())


@admin.register(Dataset)
class DatasetAdmin(
    AdminFiltersMixin,
    ExtraButtonsMixin,
    DisplayAllMixin,
    AdminActionPermMixin,
    FileProviderAdmin,
    ModelAdmin[Dataset],
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
        return super().get_queryset(request).select_related("query", "query__target")

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def arguments(self, obj: "Any") -> str:
        return obj.info.get("arguments")

    def dataset_type(self, obj: "Any") -> str:
        return obj.info.get("type")

    def target_type(self, obj: "Any") -> str:
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


@admin.register(Formatter)
class FormatterAdmin(
    ExtraButtonsMixin,
    DisplayAllMixin,
    AdminActionPermMixin,
    ModelAdmin[Formatter],
):
    list_display = ("name", "strategy", "content_type")
    search_fields = ("name",)
    list_filter = ("processor",)
    change_form_template = None
    autocomplete_fields = ("country_office", "template")

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
                    fmt: Formatter = self.object
                    dataset: Dataset = form.cleaned_data["dataset"]
                    results = fmt.render({"dataset": dataset})
                    return HttpResponse(results, content_type=fmt.content_type)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)
        context["form"] = form
        return render(request, "admin/power_query/formatter/test.html", context)


@admin.register(ReportTemplate)
class ReportTemplateAdmin(AdminFiltersMixin, ExtraButtonsMixin, AdminActionPermMixin, ModelAdmin[ReportTemplate]):
    list_display = (
        "name",
        "doc",
        "file_suffix",
    )
    search_fields = ("name",)
    list_filter = ("file_suffix",)
    autocomplete_fields = ("country_office",)

    @button()
    def preview(self, request: "HttpRequest", pk: int) -> HttpResponse:
        context = self.get_common_context(request, pk)
        if request.method == "POST":
            form = SelectDatasetForm(request.POST)
            if form.is_valid():
                processor: "Type[ProcessorStrategy]" = import_string(form.cleaned_data["processor"])
                fmt = Formatter(
                    template=self.object,
                    processor=processor,
                    code="",
                )
                content = processor(fmt).process({"dataset": form.cleaned_data["dataset"]})
                return HttpResponse(content, content_type=processor.content_type)
        else:
            form = SelectDatasetForm()
        context["form"] = form
        return render(request, "admin/power_query/reporttemplate/preview.html", context)


@admin.register(ReportConfiguration)
class ReportConfigurationAdmin(
    AdminFiltersMixin,
    CeleryEnabledMixin,
    LinkedObjectsMixin,
    ExtraButtonsMixin,
    AdminActionPermMixin,
    ModelAdmin[ReportConfiguration],
):
    list_display = ("name", "country_office", "updated_on", "last_run", "owner", "schedule", "compress", "protect")
    autocomplete_fields = ("query", "owner")
    filter_horizontal = ["limit_access_to", "formatters", "notify_to"]
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
    search_fields = ("name", "query__name")
    ordering = ("-updated_on",)
    change_form_template = "admin/power_query/report/change_form.html"
    date_hierarchy = "last_run"
    linked_objects_hide_empty = False
    object: "ReportConfiguration"

    def has_change_permission(self, request: HttpRequest, obj: "Any|None" = None) -> bool:
        return request.user.is_superuser or bool(obj and obj.owner == request.user)

    def get_changeform_initial_data(self, request: HttpRequest) -> "Dict[str, Any]":
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
            if len(results) == 1 and isinstance(results[0][0], BaseException):
                self.message_user(request, results[0][1], messages.ERROR)
                results = []
            elif len(errors) == 0:
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
    ModelAdmin[Parametrizer],
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
    ModelAdmin[ReportDocument],
):
    list_display = ("title", "content_type", "report", "file", "compressed", "protected")
    list_filter = (("report", AutoCompleteFilter), "report__compress", "report__protect")
    search_fields = ("title",)
    filter_horizontal = ("limit_access_to",)
    date_hierarchy = "dataset__last_run"
    readonly_fields = ("arguments", "report", "dataset", "content_type", "formatter", "info", "size")

    def get_queryset(self, request: HttpRequest) -> "QuerySet[ReportDocument]":
        return super().get_queryset(request)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    @button()
    def download(self, request: HttpRequest, pk: str) -> HttpResponse | StreamingHttpResponse:
        doc = self.get_object(request, pk)
        return download_media(doc.file.path, response_class=HttpResponse)

    @button()
    def resend_password(self, request: "AuthHttpRequest", pk: str) -> HttpResponse:
        obj: ReportDocument = self.get_object(request, pk)
        s = send_document_password(request.user, obj)
        self.message_user(request, f"{s}")


@admin.register(ChartPage)
class ChartPageAdmin(
    AdminFiltersMixin,
    LinkedObjectsMixin,
    ExtraButtonsMixin,
    DisplayAllMixin,
    AdminActionPermMixin,
    ModelAdmin[ChartPage],
):
    list_display = ("title", "query", "country_office", "template")
