from typing import Any, TYPE_CHECKING, TypeVar

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.signing import get_cookie_signer
from django.db.models import Model
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.utils.functional import cached_property
from django.views import View
from django.views.generic import TemplateView

import django_stubs_ext

from hope_country_report.apps.core.models import CountryOffice
from hope_country_report.apps.tenant.config import conf
from hope_country_report.apps.tenant.forms import SelectTenantForm

django_stubs_ext.monkeypatch()

if TYPE_CHECKING:
    _M = TypeVar("_M", bound=Model, covariant=True)


class SelectedOfficeMixin(LoginRequiredMixin, View):
    @cached_property
    def selected_office(self) -> CountryOffice:
        try:
            if self.request.user.is_superuser:
                co = CountryOffice.objects.get(slug=self.kwargs["co"])
            else:
                co = CountryOffice.objects.filter(userrole__user=self.request.user, slug=self.kwargs["co"])[0]
            return co
        except (CountryOffice.DoesNotExist, IndexError):
            raise PermissionDenied

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        kwargs["view"] = self
        kwargs["view_name"] = self.__class__.__name__
        kwargs["selected_office"] = self.selected_office
        kwargs["tenant_form"] = SelectTenantForm(request=self.request, initial={"tenant": self.selected_office})
        return super().get_context_data(**kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse | StreamingHttpResponse:
        response = super().get(request, *args, **kwargs)
        signer = get_cookie_signer()
        response.set_cookie(conf.COOKIE_NAME, signer.sign(self.selected_office.slug))
        return response


class OfficeTemplateView(SelectedOfficeMixin, TemplateView):
    template_name = "web/office/index.html"
