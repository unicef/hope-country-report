import factory

from hope_country_report.apps.stream.models import Event
from testutils.factories.base import AutoRegisterModelFactory
from testutils.factories.user import CountryOfficeFactory


class EventFactory(AutoRegisterModelFactory):
    class Meta:
        model = Event
        django_get_or_create = ("name",)

    name = factory.Faker("word")
    enabled = True
    office = factory.SubFactory(CountryOfficeFactory)
    query = factory.SubFactory(
        "testutils.factories.power_query.QueryFactory",
        country_office=factory.SelfAttribute("..office"),
    )
