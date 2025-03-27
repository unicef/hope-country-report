from django.contrib.admin import ModelAdmin
from django.db.models import Model

from ._base import get_filters_for_model, HopeModelAdmin


def modeladmin_factory(model: type[Model], **custom: dict[str, str]) -> type[ModelAdmin]:
    params = {"list_filter": get_filters_for_model(model)}
    params.update(custom)
    return type(f"Auto{model._meta.model_name}Admin", (HopeModelAdmin,), params)  # noqa
