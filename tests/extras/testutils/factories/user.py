from uuid import uuid4

from django.contrib.admin.models import LogEntry
from django.utils.text import slugify

import factory
from social_django.models import UserSocialAuth
from testutils.factories.base import AutoRegisterModelFactory

from hope_country_report.apps.core.models import CountryOffice, User, UserRole

from .django_auth import GroupFactory
from .hope import BusinessAreaFactory


class UserFactory(AutoRegisterModelFactory):
    username = factory.Sequence(lambda n: "m%03d@example.com" % n)
    first_name = "Jhon"
    last_name = "Doe"
    email = factory.Sequence(lambda n: "m%03d@example.com" % n)
    is_superuser = False
    is_active = True
    is_staff = False

    _password = "password"
    _original_params = {}

    class Meta:
        model = User
        django_get_or_create = ("username", "is_active", "is_staff")

    @classmethod
    def _generate(cls, strategy, params):
        instance = super()._generate(strategy, params)
        instance._password = UserFactory._password
        return instance

    @factory.post_generation
    def post1(obj, create, extracted, **kwargs):
        obj._password = UserFactory._password
        obj.set_password(obj._password)
        obj.save()


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
    class Meta:
        model = CountryOffice
        django_get_or_create = ("name",)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Create the prerequisite data here.
        # Use `UserFactory.create_batch(n)` if multiple instances are needed.
        ba = BusinessAreaFactory()
        values = {
            "hope_id": str(ba.id),
            "name": ba.name,
            "active": ba.active,
            "code": ba.code,
            "long_name": ba.long_name,
            "region_code": ba.region_code,
            "slug": slugify(ba.name),
        }
        co = CountryOffice(**values)
        co.save()

        return co


class UserRoleFactory(AutoRegisterModelFactory):
    country_office = factory.SubFactory(CountryOfficeFactory)
    group = factory.SubFactory(GroupFactory)
    user = factory.SubFactory(UserFactory)
    expires = None

    class Meta:
        model = UserRole
        django_get_or_create = ("country_office", "group", "user")
