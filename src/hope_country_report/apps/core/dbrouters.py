from typing import Any

from django.conf import settings
from django.db.models import Model


class DbRouter:
    @staticmethod
    def select_db(model: type[Model] | None) -> str | None:
        if model._meta.proxy:
            model = model._meta.proxy_for_model
        return settings.DATABASE_APPS_MAPPING.get(model._meta.app_label)  # type: ignore[no-any-return]

    def db_for_read(self, model: type[Model] | None, **hints: Any) -> str | None:
        return DbRouter.select_db(model)

    def db_for_write(self, model: type[Model] | None, **hints: Any) -> str | None:
        return DbRouter.select_db(model)

    def allow_migrate(self, db: str, app_label: str, model_name: str | None = None, **hints: Any) -> bool:
        if db in {"hope", "hope_ro"}:
            return False
        if db == "default" and app_label not in settings.DATABASE_APPS_MAPPING:
            return True

        mapped_db = settings.DATABASE_APPS_MAPPING.get(app_label)
        return bool(mapped_db == db)
