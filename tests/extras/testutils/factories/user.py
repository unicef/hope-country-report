from uuid import uuid4

from django.contrib.admin.models import LogEntry
from django.utils.text import slugify

import factory
from social_django.models import UserSocialAuth
from testutils.factories.base import AutoRegisterModelFactory

from hope_country_report.apps.core.models import CountryOffice, DATE_FORMATS, TIME_FORMATS, User, UserRole

from .django_auth import GroupFactory
from .hope import BusinessAreaFactory


class UserFactory(AutoRegisterModelFactory):
    _password = "password"
    username = factory.Sequence(lambda n: "m%03d@example.com" % n)
    password = factory.django.Password(_password)
    email = factory.Sequence(lambda n: "m%03d@example.com" % n)
    language = "en"
    date_format = DATE_FORMATS[0][0]
    time_format = TIME_FORMATS[0][0]
    first_name = "Jhon"
    last_name = "Doe"
    is_superuser = False
    is_active = True
    is_staff = False

    class Meta:
        model = User
        django_get_or_create = ("username", "is_active", "is_staff")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        ret = super()._create(model_class, *args, **kwargs)
        ret._password = cls._password
        return ret


class SuperUserFactory(UserFactory):
    username = factory.Sequence(lambda n: "superuser%03d@example.com" % n)
    email = factory.Sequence(lambda n: "superuser%03d@example.com" % n)
    is_superuser = True
    is_staff = True
    is_active = True


class SocialAuthUserFactory(UserFactory):
    @factory.post_generation
    def sso(obj, create, extracted, **kwargs):
        UserSocialAuth.objects.get_or_create(user=obj, provider="test", uid=uuid4())


class LogEntryFactory(AutoRegisterModelFactory):
    action_flag = 1
    user = factory.SubFactory(UserFactory, username="admin")

    class Meta:
        model = LogEntry


class CountryOfficeFactory(AutoRegisterModelFactory):
    name = factory.Iterator(["Afghanistan", "Ukraine", "Niger", "South Sudan"])
    code = factory.Sequence(lambda x: str(x))

    class Meta:
        model = CountryOffice
        django_get_or_create = ("name",)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if ba := kwargs.pop("business_area", None):
            pass
        else:
            ba = BusinessAreaFactory(name=kwargs["name"])

        values = {
            "hope_id": str(ba.id),
            "name": ba.name,
            "active": ba.active,
            "code": kwargs["code"],
            "long_name": ba.long_name,
            "region_code": ba.region_code,
            "slug": slugify(ba.name),
        }
        if cls._meta.django_get_or_create:
            return cls._get_or_create(model_class, *args, **values)

        manager = cls._get_manager(model_class)
        return manager.create(*args, **values)


class UserRoleFactory(AutoRegisterModelFactory):
    country_office = factory.SubFactory(CountryOfficeFactory)
    group = factory.SubFactory(GroupFactory)
    user = factory.SubFactory(UserFactory)
    expires = None

    class Meta:
        model = UserRole
        django_get_or_create = ("country_office", "group", "user")
