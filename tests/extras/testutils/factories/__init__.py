import typing

from .base import AutoRegisterModelFactory, factories_registry, TAutoRegisterModelFactory
from .contenttypes import *
from .django_auth import *
from .django_celery_beat import *
from .user import *


def get_factory_for_model(_model) -> typing.Type[TAutoRegisterModelFactory]:
    class Meta:
        model = _model

    if _model in factories_registry:
        return factories_registry[_model]
    return type(f"{_model._meta.model_name}Factory", (AutoRegisterModelFactory,), {"Meta": Meta})
