import uuid

import factory
from testutils.factories import AutoRegisterModelFactory

from hope_country_report.apps.hope.models import BusinessArea


class BusinessAreaFactory(AutoRegisterModelFactory):
    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Iterator(["Afghanistan", "Ukraine", "Niger", "South Sudan"])
    code = factory.Sequence(lambda x: str(x).zfill(4))

    class Meta:
        model = BusinessArea
