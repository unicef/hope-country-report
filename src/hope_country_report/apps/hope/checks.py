from typing import Any, List

from django.apps import AppConfig, apps
from django.core.checks import Error, register, Warning


@register()
def check_models(app_configs: "AppConfig", **kwargs: "Any") -> "List[Error]":
    errors = []

    for app_config in (apps.app_configs["hope"], apps.app_configs["power_query"]):
        for model in app_config.get_models():
            if not model.Tenant.tenant_filter_field:  # pragma: no branch
                errors.append(
                    Error(
                        f"{model} does not have Tenant.tenant_filter_field",
                        # hint="TENANT_MODEL must be a valid Django Model",
                        obj=model,
                        id="tenant.E001",
                    )
                )
            elif model.Tenant.tenant_filter_field == "__notset__":
                errors.append(
                    Warning(
                        f"{model} does not have restrictions enabled",
                        obj=model,
                        id="tenant.E002",
                    )
                )
    return errors
