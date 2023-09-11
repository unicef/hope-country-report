from django.apps import AppConfig
from django.core.checks import Error, register

from tenant_admin.options import MainTenantModelAdmin


@register()
def check_tenant_model(app_configs: AppConfig, **kwargs):
    errors = []
    from .config import conf

    try:
        conf.tenant_model
    except LookupError:
        errors.append(
            Error(
                "Invalid value for settings.TENANT_TENANT_MODEL. '%s' is not a valid Django Model"
                % getattr(conf, "TENANT_MODEL", None),
                hint="TENANT_MODEL must be a valid Django Model",
                obj="settings.TENANT_MODEL",
                id="tenant_admin.E001",
            )
        )
    return errors


@register()
def check_main_tenant_admin(app_configs, **kwargs):
    errors = []

    try:
        from tenant_admin.sites import site

        ma = site.get_tenant_modeladmin()
        if not isinstance(ma, MainTenantModelAdmin):
            errors.append(
                Error(
                    "ModelAdmin that manage Main Tenant Model should use `MainTenantModelAdmin`",
                    hint="Update '%s' to inherit from %s" % (ma, MainTenantModelAdmin),
                    obj=ma.__class__.__name__,
                    id="tenant_admin.E002",
                )
            )
    except KeyError:
        pass
    return errors
