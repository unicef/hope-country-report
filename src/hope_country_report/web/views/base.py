from typing import TYPE_CHECKING, Any, TypeVar

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.signing import get_cookie_signer
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.utils.functional import cached_property
from django.views import View
from django.views.generic import TemplateView

from hope_country_report.apps.core.models import CountryOffice
from hope_country_report.apps.tenant.config import conf
from hope_country_report.apps.tenant.forms import SelectTenantForm
from hope_country_report.state import state

if TYPE_CHECKING:
    from django.db.models import Model

    _M = TypeVar("_M", bound=Model, covariant=True)


class SelectedOfficeMixin(LoginRequiredMixin, View):
    @cached_property
    def selected_office(self) -> CountryOffice:
        try:
            if self.request.user.is_superuser:
                co = CountryOffice.objects.get(slug=self.kwargs["co"])
            else:
                # Resolve through the expiry-aware tenant backend so an expired
                # UserRole can no longer reach the office's reports/documents.
                co = conf.auth.get_allowed_tenants(self.request).filter(slug=self.kwargs["co"]).first()
                if co is None:
                    raise PermissionDenied
        except CountryOffice.DoesNotExist:
            raise PermissionDenied
        state.tenant = co
        return co

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            self.selected_office
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        kwargs["view"] = self
        kwargs["view_name"] = self.__class__.__name__
        kwargs["selected_office"] = self.selected_office
        kwargs["tenant_form"] = SelectTenantForm(request=self.request, initial={"tenant": self.selected_office})
        return super().get_context_data(**kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse | StreamingHttpResponse:
        response = super().get(request, *args, **kwargs)
        signer = get_cookie_signer()
        response.set_cookie(
            conf.COOKIE_NAME,
            signer.sign(self.selected_office.slug),
            secure=settings.SESSION_COOKIE_SECURE,
            httponly=True,
            samesite="Lax",
        )
        return response


class OfficeTemplateView(SelectedOfficeMixin, TemplateView):
    template_name = "web/office/index.html"
