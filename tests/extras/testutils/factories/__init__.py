from django.db.models.fields import UUIDField

from .base import AutoRegisterModelFactory, factories_registry, HopeAutoRegisterModelFactory, TAutoRegisterModelFactory

# isort: split
from .adv_filters import AdvancedFilterFactory as AdvancedFilterFactory
from .contenttypes import *
from .django_auth import *
from .django_celery_beat import *
from .hope import *
from .power_query import *
from .user import *


def get_factory_for_model(_model) -> type[TAutoRegisterModelFactory]:
    class Meta:
        model = _model

    bases = (AutoRegisterModelFactory,)
    if _model in factories_registry:
        return factories_registry[_model]
    if _model._meta.app_label in ["hope"] and isinstance(_model._meta.get_field("id"), UUIDField):
        bases = (HopeAutoRegisterModelFactory,)

    return type(f"{_model._meta.model_name}Factory", bases, {"Meta": Meta})
