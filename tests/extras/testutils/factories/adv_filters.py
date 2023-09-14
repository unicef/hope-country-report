import factory
from advanced_filters.models import AdvancedFilter

from .base import AutoRegisterModelFactory
from .user import UserFactory


class AdvancedFilterFactory(AutoRegisterModelFactory):
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = AdvancedFilter
