import logging

import django.http
from django.core.exceptions import ObjectDoesNotExist
from django.core.signing import get_cookie_signer
from django.db.models import Model
from django.http import HttpResponse

from . import state
from .config import AppSettings

logger = logging.getLogger(__name__)


class BaseTenantStrategy:
    pk = "pk"

    def __init__(self, config: AppSettings):
        self.config = config
        self._selected_tenant = None
        self._selected_tenant_value = ""

    def set_selected_tenant(self, response: HttpResponse, instance: Model) -> None:
        signer = get_cookie_signer()
        response.set_cookie(self.config.COOKIE_NAME, signer.sign(getattr(instance, self.pk)))

    def get_selected_tenant(self, request: "django.http.HttpRequest") -> Model:
        cookie_value = request.COOKIES.get(self.config.COOKIE_NAME)
        signer = get_cookie_signer()
        if (self._selected_tenant_value != cookie_value) or (self._selected_tenant is None):
            try:
                filters = {self.pk: signer.unsign(cookie_value)}
                self._selected_tenant_value = cookie_value
                self._selected_tenant = self.config.auth.get_allowed_tenants(request).get(**filters)
            except ObjectDoesNotExist:
                self._selected_tenant = None
            except TypeError:
                self._selected_tenant = None
            except Exception as e:  # pragma: no cover
                logger.exception(e)
                self._selected_tenant = None
        state.tenant = self._selected_tenant
        return self._selected_tenant
