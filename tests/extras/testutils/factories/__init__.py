import factory
from django.core.exceptions import FieldDoesNotExist
from django.db.models import UUIDField

from .base import AutoRegisterModelFactory, HopeAutoRegisterModelFactory, TAutoRegisterModelFactory, factories_registry

# isort: split
from .adv_filters import AdvancedFilterFactory as AdvancedFilterFactory
from .contenttypes import *  # noqa :F401,F403
from .django_auth import *  # noqa :F401,F403
from .django_celery_beat import *  # noqa :F401,F403
from .hope import *  # noqa :F401,F403
from .power_query import *  # noqa :F401,F403
from .user import *  # noqa :F401,F403


def get_factory_for_model(_model) -> type[TAutoRegisterModelFactory]:
    class Meta:
        model = _model

    factory_attrs = {"Meta": Meta}
    bases = (AutoRegisterModelFactory,)
    if _model in factories_registry:
        return factories_registry[_model]
    try:
        has_uuid_id = isinstance(_model._meta.get_field("id"), UUIDField)
    except FieldDoesNotExist:
        has_uuid_id = False

    if _model._meta.app_label in ["hope"] and has_uuid_id:
        bases = (HopeAutoRegisterModelFactory,)

    pk = _model._meta.pk
    if pk and not pk.auto_created and pk.get_internal_type() == "IntegerField":
        factory_attrs[pk.name] = factory.Sequence(lambda n: n + 1)

    return type(f"{_model._meta.model_name}Factory", bases, factory_attrs)
