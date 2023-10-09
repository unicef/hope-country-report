from typing import Any, List

from django.apps import AppConfig, apps
from django.core.checks import Error, register


@register()
def check_models(app_configs: "AppConfig", **kwargs: "Any") -> "List[Error]":
    errors = []
    # app_config = apps.app_configs["hope"]

    for app_config in (apps.app_configs["hope"], apps.app_configs["power_query"]):
        for model in app_config.get_models():
            try:
                if not model.Tenant.tenant_filter_field:
                    raise Exception
            except Exception:
                errors.append(
                    Error(
                        f"{model} does not have Tenant.tenant_filter_field",
                        # hint="TENANT_MODEL must be a valid Django Model",
                        obj=model,
                        id="tenant.E001",
                    )
                )
    return errors
