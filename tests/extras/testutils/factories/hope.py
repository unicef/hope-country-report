import uuid

import factory
from factory import fuzzy, post_generation
from faker import Faker
from testutils.factories import AutoRegisterModelFactory

from hope_country_report.apps.hope import models

faker = Faker()


class BusinessAreaFactory(AutoRegisterModelFactory):
    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Iterator(["Afghanistan", "Ukraine", "Niger", "South Sudan"])
    code = factory.Sequence(lambda x: str(x).zfill(4))

    class Meta:
        model = models.BusinessArea


class CountryFactory(AutoRegisterModelFactory):
    name = factory.Iterator(["Afghanistan", "Ukraine", "Niger", "South Sudan"])
    short_name = factory.Iterator(["Afghanistan", "Ukraine", "Niger", "South Sudan"])
    iso_code2 = factory.Iterator(["af", "ua", "ne", "ss"])
    iso_code3 = factory.Iterator(["afg", "ukr", "nga", "sso"])
    iso_num = factory.Iterator(["004", "562", "728", "728"])

    class Meta:
        model = models.Country


class AreaTypeFactory(AutoRegisterModelFactory):
    name = factory.LazyFunction(faker.domain_word)
    country = factory.SubFactory(CountryFactory, parent=None)
    area_level = fuzzy.FuzzyChoice([1, 2, 3, 4])
    parent = None

    class Meta:
        model = models.AreaType
        django_get_or_create = ("name", "country", "area_level")


class AreaFactory(AutoRegisterModelFactory):
    name = factory.Sequence(lambda x: "Area #%s" % x)
    area_type = factory.SubFactory(AreaTypeFactory, parent=None)
    parent = None

    class Meta:
        model = models.Area


class HouseholdFactory(AutoRegisterModelFactory):
    id = factory.Sequence(lambda x: str(x))
    business_area = factory.SubFactory(BusinessAreaFactory)

    class Meta:
        model = models.Household

    @post_generation
    def set_head_of_household(self, create, extracted, **kwargs):
        if not create:
            return
        self.head_of_household = IndividualFactory(household=self)
        self.save()


class IndividualFactory(AutoRegisterModelFactory):
    household = factory.SubFactory(HouseholdFactory)

    class Meta:
        model = models.Individual
