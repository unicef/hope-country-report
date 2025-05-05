from typing import Any, TYPE_CHECKING, TypeVar

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AbstractBaseUser
from django.core.signing import get_cookie_signer
from django.db.models import Model, QuerySet
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView

from hope_country_report.apps.core.models import CountryOffice, User
from hope_country_report.apps.tenant.config import conf
from hope_country_report.web.forms import UserProfileForm

from .base import SelectedOfficeMixin

if TYPE_CHECKING:
    from django.http import HttpResponse
    from django.views.generic.edit import _ModelFormT

    from hope_country_report.types.http import AuthHttpRequest

    _M = TypeVar("_M", bound=Model, covariant=True)


class UserProfileView(SelectedOfficeMixin, UpdateView[User, Any]):
    request: "AuthHttpRequest"
    form_class = UserProfileForm
    model = User
    template_name = "web/office/profile.html"
    success_url = "."

    @cached_property
    def selected_office(self) -> CountryOffice:
        signer = get_cookie_signer()
        return CountryOffice.objects.get(slug=signer.unsign(str(self.request.COOKIES.get(conf.COOKIE_NAME))))

    def get_object(self, queryset: QuerySet[AbstractBaseUser] | None = None) -> "User":
        return self.request.user

    def form_valid(self, form: "_ModelFormT") -> "HttpResponse":
        response = super().form_valid(form)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, self.request.user.language)
        messages.success(self.request, _("Saved."))
        return response
