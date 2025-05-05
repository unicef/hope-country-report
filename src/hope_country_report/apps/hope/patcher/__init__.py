from typing import Any, TYPE_CHECKING

import logging
from functools import partial, partialmethod

from django.apps import AppConfig, apps
from django.db import models

from hope_country_report.apps.hope import models as hope_models

if TYPE_CHECKING:
    from django.db.models import Model

    from hope_country_report.apps.hope.models import HopeModel
    from hope_country_report.types.django import AnyModel


logger = logging.getLogger(__name__)


def label(attr: str, self: "type[AnyModel]") -> str:
    return str(getattr(self, attr))


def create_alias(model: "type[AnyModel]", aliases: dict[str, str]) -> None:
    for related, business_name in aliases:
        r: Any = getattr(model, related)
        setattr(model, business_name, r)


def add_m2m(
    master: "type[Model]", name: str, detail: "type[Model]", through: "type[AnyModel]", related_name: "str|None" = None
) -> None:
    models.ManyToManyField(
        detail,
        through=through,
        related_name=related_name,
    ).contribute_to_class(master, name)


def patch() -> None:
    TENANT_MAPPING: "dict[type[AnyModel], str]" = {
        hope_models.BusinessArea: "id",
        hope_models.Household: "business_area",
        # hope_model.AccountIncompatibleroles: "__all__",
        # hope_model.AccountRole: "__all__",
        # hope_model.AccountPartner: "__all__",
        # hope_model.AccountUser: "__all__",
        # hope_model.AccountUsergroup: "__all__",
        # hope_model.AccountUserGroups: "__all__",
        # hope_model.AccountUserUserPermissions: "__all__",
    }
    ORDERING: "dict[type[AnyModel], list | tuple]" = {
        hope_models.BusinessArea: ["name"],
        hope_models.Household: ["unicef_id"],
    }

    appconf: AppConfig = apps.get_app_config("hope")
    model: HopeModel

    for model in appconf.get_models():
        for attr in ["name", "username", "unicef_id"]:
            if hasattr(model, attr):
                model.__str__ = partialmethod(partial(label, attr))
                break
        if model in TENANT_MAPPING:
            model.Tenant.tenant_filter_field = TENANT_MAPPING[model]
        else:
            model.Tenant.tenant_filter_field = "__notset__"

        if model in ORDERING:
            model._meta.ordering = ORDERING[model]
        else:
            model._meta.ordering = ["pk"]

    # from . import household, payments
    from . import ba  # noqa
