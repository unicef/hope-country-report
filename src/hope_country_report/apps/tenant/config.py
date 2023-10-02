from __future__ import annotations

from functools import cached_property
from typing import Any, TYPE_CHECKING, Union

from django.core.signals import setting_changed
from django.db.models import Model
from django.utils.module_loading import import_string

if TYPE_CHECKING:
    from .auth import BaseTenantAuth
    from .strategy import BaseTenantStrategy


class AppSettings:
    COOKIE_NAME: str
    TENANT_MODEL: Model
    STRATEGY: "BaseTenantStrategy"
    AUTH: "BaseTenantAuth"
    defaults = {
        "TENANT_MODEL": None,
        "COOKIE_NAME": "selected_tenant",
        "STRATEGY": "tenant_admin.strategy.DefaultStrategy",
        "AUTH": "tenant_admin.auth.BaseTenantAuth",
    }

    def __init__(self, prefix: str):
        """
        Loads our settings from django.conf.settings, applying defaults for any
        that are omitted.
        """
        self.prefix = prefix
        from django.conf import settings

        for name, default in self.defaults.items():
            prefixed_name = self.prefix + "_" + name
            value = getattr(settings, prefixed_name, default)
            self._set_attr(prefixed_name, value)
            setattr(settings, prefixed_name, value)
            setting_changed.send(self.__class__, setting=prefixed_name, value=value, enter=True)

        setting_changed.connect(self._on_setting_changed)

    def _set_attr(self, prefixed_name: str, value: Any) -> None:
        name = prefixed_name[len(self.prefix) + 1 :]
        setattr(self, name, value)

    @cached_property
    def strategy(self) -> "BaseTenantStrategy":
        from .strategy import BaseTenantStrategy

        return BaseTenantStrategy(self)
        # return import_string(self.STRATEGY)(self)  # type: ignore[no-any-return]

    @cached_property
    def auth(self) -> "BaseTenantAuth":
        from .auth import BaseTenantAuth

        return BaseTenantAuth()
        return import_string(self.AUTH)()  # type: ignore[no-any-return]

    @cached_property
    def tenant_model(self) -> Union[Model, type]:
        from django.apps import apps

        if not self.TENANT_MODEL:
            raise ValueError(f"Please set settings.{self.prefix}_TENANT_MODEL")
        return apps.get_model(self.TENANT_MODEL)  # type ignore [return-value,attr-defined]

    def _on_setting_changed(self, sender: Model, setting: str, value: Any, **kwargs) -> None:
        if setting.startswith(self.prefix):
            self._set_attr(setting, value)
        for attr in ["tenant_model", "auth", "strategy"]:
            try:
                delattr(self, attr)
            except AttributeError:
                pass


conf = AppSettings("TENANT")
