import uuid

from django.utils.text import slugify

import factory
import pytz
from factory import fuzzy, post_generation
from faker import Faker
from testutils.factories import AutoRegisterModelFactory, HopeAutoRegisterModelFactory

from hope_country_report.apps.hope import models as hope_models

faker = Faker()


class BusinessAreaFactory(HopeAutoRegisterModelFactory):
    # id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Iterator(["Afghanistan", "Ukraine", "Niger", "South Sudan"])
    code = factory.Sequence(lambda x: str(x).zfill(4))
    is_split = False
    parent = None

    class Meta:
        model = hope_models.BusinessArea
        django_get_or_create = ("name",)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs.setdefault("long_name", kwargs["name"])
        kwargs.setdefault("slug", slugify(kwargs["name"]))
        if cls._meta.django_get_or_create:
            return cls._get_or_create(model_class, *args, **kwargs)

        manager = cls._get_manager(model_class)
        return manager.create(*args, **kwargs)

    @post_generation
    def add_country(self, create, extracted, **kwargs):
        if "country" in kwargs:
            self.countries.add(kwargs["country"])
        else:
            self.countries.add(CountryFactory(name=self.name))


COUNTRIES = {
    "Afghanistan": {"iso_code2": "af", "iso_code3": "afg", "iso_num": "004"},
    "Ukraine": {"iso_code2": "ua", "iso_code3": "ukr", "iso_num": "804"},
    "Niger": {"iso_code2": "ss", "iso_code3": "nga", "iso_num": "562"},
    "South Sudan": {"iso_code2": "ne", "iso_code3": "sso", "iso_num": "728"},
    "Sudan": {"iso_code2": "sd", "iso_code3": "sdn", "iso_num": "729"},
}


class CountryFactory(AutoRegisterModelFactory):
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Iterator(["Afghanistan", "Ukraine", "Niger", "South Sudan"])
    # short_name = factory.Iterator(["Afghanistan", "Ukraine", "Niger", "South Sudan"])
    # iso_code2 = factory.Iterator(["af", "ua", "ne", "ss"])
    # iso_code3 = factory.Iterator(["afg", "ukr", "nga", "sso"])
    # iso_num = factory.Iterator(["004", "804", "562", "728"])
    parent = None
    lft = 0
    rght = 0
    level = 0
    tree_id = 0

    class Meta:
        model = hope_models.Country
        django_get_or_create = ("name",)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        name = kwargs["name"]
        kwargs.update(**COUNTRIES[name])
        # kwargs.setdefault("long_name", kwargs["name"])
        # kwargs.setdefault("slug", slugify(name))
        if cls._meta.django_get_or_create:
            return cls._get_or_create(model_class, *args, **kwargs)

        manager = cls._get_manager(model_class)
        return manager.create(*args, **kwargs)


class BusinessareaCountriesFactory(HopeAutoRegisterModelFactory):
    id = factory.Sequence(lambda x: x)
    businessarea = factory.SubFactory(BusinessAreaFactory)
    country = factory.SubFactory(CountryFactory)

    class Meta:
        model = hope_models.BusinessareaCountries


class AreaTypeFactory(AutoRegisterModelFactory):
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.LazyFunction(faker.domain_word)
    country = factory.SubFactory(CountryFactory, parent=None)
    area_level = fuzzy.FuzzyChoice([1, 2, 3, 4])
    parent = None

    class Meta:
        model = hope_models.Areatype
        django_get_or_create = ("name", "country", "area_level")


class AreaFactory(AutoRegisterModelFactory):
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda x: f"Area #{x}")
    area_type = factory.SubFactory(AreaTypeFactory, parent=None)
    parent = None

    class Meta:
        model = hope_models.Area


class DataCollectingTypeFactory(AutoRegisterModelFactory):
    id = factory.Sequence(lambda x: x)
    code = factory.Iterator(["hh only", "full", "partial"])

    class Meta:
        model = hope_models.DataCollectingType


class DatacollectingtypeLimitToFactory(AutoRegisterModelFactory):
    id = factory.Sequence(lambda x: x)

    class Meta:
        model = hope_models.DatacollectingtypeLimitTo


class DatacollectingtypeCompatibleTypesFactory(AutoRegisterModelFactory):
    id = factory.Sequence(lambda x: x)

    class Meta:
        model = hope_models.DatacollectingtypeCompatibleTypes


class ProgramFactory(AutoRegisterModelFactory):
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    business_area = factory.SubFactory(BusinessAreaFactory)
    # data_collecting_type = factory.SubFactory(DataCollectingTypeFactory)
    start_date = factory.Faker("date_time")
    end_date = factory.Faker("date_time")

    class Meta:
        model = hope_models.Program


class CycleFactory(AutoRegisterModelFactory):
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    program = factory.SubFactory(ProgramFactory)
    start_date = factory.Faker("date_time")
    end_date = factory.Faker("date_time")

    class Meta:
        model = hope_models.ProgramCycle


class IndividualFactory(AutoRegisterModelFactory):
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    full_name = factory.Faker("name")
    business_area = factory.SubFactory(BusinessAreaFactory)
    first_registration_date = factory.Faker("date_time")
    last_registration_date = factory.Faker("date_time")
    household = None

    class Meta:
        model = hope_models.Individual


class HouseholdFactory(AutoRegisterModelFactory):
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    unicef_id = factory.Sequence(lambda x: str((x + 1) * 1000))
    business_area = factory.SubFactory(BusinessAreaFactory)
    head_of_household = factory.SubFactory(IndividualFactory)
    program = factory.SubFactory(ProgramFactory)
    first_registration_date = factory.Faker("date_time", tzinfo=pytz.UTC)
    last_registration_date = factory.Faker("date_time", tzinfo=pytz.UTC)
    copied_from = None
    country = None
    country_origin = None
    admin_area = None
    admin1 = None
    admin2 = None
    admin3 = None
    admin4 = None
    household_collection = None

    class Meta:
        model = hope_models.Household
        django_get_or_create = ("id",)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs["head_of_household"].business_area = kwargs["business_area"]
        kwargs["program"].business_area = kwargs["business_area"]
        if cls._meta.django_get_or_create:
            return cls._get_or_create(model_class, *args, **kwargs)

        manager = cls._get_manager(model_class)
        return manager.create(*args, **kwargs)

    @post_generation
    def set_head_of_household(self, create, extracted, **kwargs):
        if not create:
            return
        self.head_of_household.household = self
        self.head_of_household.business_area = self.business_area
        self.head_of_household.save()


class IndividualRoleInHouseholdFactory(AutoRegisterModelFactory):
    individual = factory.SubFactory(IndividualFactory)
    household = factory.SubFactory(HouseholdFactory)

    class Meta:
        model = hope_models.Individualroleinhousehold
