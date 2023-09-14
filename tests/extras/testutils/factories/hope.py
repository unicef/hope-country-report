import uuid

import factory
from testutils.factories import AutoRegisterModelFactory

from hope_country_report.apps.hope.models import BusinessArea


class BusinessAreaFactory(AutoRegisterModelFactory):
    id = factory.LazyFunction(uuid.uuid4)

    class Meta:
        model = BusinessArea
