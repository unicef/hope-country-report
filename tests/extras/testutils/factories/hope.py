import uuid

from django.utils.text import slugify

import factory
import pytz
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
        django_get_or_create = ("name",)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs["id"] = slugify(kwargs["name"])
        if cls._meta.django_get_or_create:
            return cls._get_or_create(model_class, *args, **kwargs)

        manager = cls._get_manager(model_class)
        return manager.create(*args, **kwargs)


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


class DataCollectingTypeFactory(AutoRegisterModelFactory):
    class Meta:
        model = models.DataCollectingType


class ProgramFactory(AutoRegisterModelFactory):
    id = factory.Sequence(lambda x: str(x))
    business_area = factory.SubFactory(BusinessAreaFactory)
    # data_collecting_type = factory.SubFactory(DataCollectingTypeFactory)
    start_date = factory.Faker("date_time")
    end_date = factory.Faker("date_time")

    class Meta:
        model = models.Program


class CycleFactory(AutoRegisterModelFactory):
    program = factory.SubFactory(ProgramFactory)
    start_date = factory.Faker("date_time")
    end_date = factory.Faker("date_time")

    class Meta:
        model = models.Cycle


class IndividualFactory(AutoRegisterModelFactory):
    id = factory.Sequence(lambda x: str(x))
    full_name = factory.Faker("name")
    business_area = factory.SubFactory(BusinessAreaFactory)
    first_registration_date = factory.Faker("date_time")
    last_registration_date = factory.Faker("date_time")
    household = None

    class Meta:
        model = models.Individual


class HouseholdFactory(AutoRegisterModelFactory):
    id = factory.Sequence(lambda x: str(x + 1))
    unicef_id = factory.Sequence(lambda x: str((x + 1) * 1000))
    business_area = factory.SubFactory(BusinessAreaFactory)
    head_of_household = factory.SubFactory(IndividualFactory)
    first_registration_date = factory.Faker("date_time", tzinfo=pytz.UTC)
    last_registration_date = factory.Faker("date_time", tzinfo=pytz.UTC)

    class Meta:
        model = models.Household

    @post_generation
    def set_head_of_household(self, create, extracted, **kwargs):
        if not create:
            return
        self.head_of_household.household = self
        self.head_of_household.business_area = self.business_area
        self.head_of_household.save()
