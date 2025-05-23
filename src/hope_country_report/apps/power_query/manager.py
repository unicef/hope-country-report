from typing import TYPE_CHECKING

import logging

from django.db.models import Q

from hope_country_report.apps.core.utils import SmartManager
from hope_country_report.apps.tenant.utils import get_selected_tenant, must_tenant

from ...state import state

# from django.db.models.manager import RelatedManager
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from ...types.pq import _PowerQueryModel


class PowerQueryManager(SmartManager["_PowerQueryModel"]):
    def get_tenant_filter(self, selected_tenant=None) -> "Q":
        _filter = Q()
        if must_tenant():
            tenant_filter_field = self.model.Tenant.tenant_filter_field
            if not tenant_filter_field:
                raise ValueError(
                    f"Set 'tenant_filter_field' on {self} or override `get_queryset()` to enable queryset filtering"
                )

            if tenant_filter_field == "__all__":
                return Q()
            active_tenant = selected_tenant or get_selected_tenant()
            if active_tenant:
                _filter = Q(**{tenant_filter_field: active_tenant})
        return _filter

    def get_queryset(self) -> "QuerySet[_PowerQueryModel]":
        flt = self.get_tenant_filter()
        if flt:
            state.filters.append(str(flt))
        return super().get_queryset().filter(flt)
