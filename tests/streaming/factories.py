import factory

from hope_country_report.apps.stream.models import Event
from tests.extras.testutils.factories.base import AutoRegisterModelFactory
from tests.extras.testutils.factories.user import CountryOfficeFactory


class EventFactory(AutoRegisterModelFactory):
    class Meta:
        model = Event
        django_get_or_create = ("name",)

    name = factory.Faker("word")
    enabled = True
    office = factory.SubFactory(CountryOfficeFactory)
    query = factory.SubFactory(
        "tests.extras.testutils.factories.power_query.QueryFactory",
        country_office=factory.SelfAttribute("..office"),
    )
    routing_key = "hcr.dataset.save"
