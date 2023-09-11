import random
import uuid
from uuid import uuid4

from django.contrib.admin.models import LogEntry

import factory
from social_django.models import UserSocialAuth
from testutils.factories.base import AutoRegisterModelFactory

from hope_country_report.apps.core.models import User


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
