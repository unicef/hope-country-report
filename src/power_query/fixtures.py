import time
from typing import Any, Dict, List, Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

import factory
from factory.django import DjangoModelFactory

from power_query.models import Dataset, Formatter, Parametrizer, Query, Report, ReportDocument


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ("username",)

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.LazyAttribute(lambda o: f"{o.first_name.lower()}.{o.last_name.lower()}_{time.time_ns()}@unicef.com")
    username = factory.LazyAttribute(lambda o: f"{o.first_name}{o.last_name}_{time.time_ns()}")

    @classmethod
    def _create(cls, model_class: Any, *args: Any, **kwargs: Any) -> get_user_model():
        manager = cls._get_manager(model_class)
        keyword_arguments = kwargs.copy()
        if "password" not in keyword_arguments:
            keyword_arguments["password"] = "password"
        return manager.create_user(*args, **keyword_arguments)


class GroupFactory(DjangoModelFactory):
    name = factory.Sequence(lambda x: f"Group{x}")

    class Meta:
        model = Group
        django_get_or_create = ("name",)


class ContentTypeFactory(DjangoModelFactory):
    class Meta:
        model = ContentType
        django_get_or_create = ("app_label", "model")


class QueryFactory(DjangoModelFactory):
    name = factory.Sequence(lambda x: f"Query{x}")
    owner = factory.SubFactory(UserFactory, is_superuser=True, is_staff=True)
    target = factory.Iterator(ContentType.objects.filter(app_label="auth", model="permission"))
    code = "result=conn.all()"

    class Meta:
        model = Query
        # django_get_or_create = ("name",)


class DatasetFactory(DjangoModelFactory):
    query = factory.SubFactory(QueryFactory)

    class Meta:
        model = Dataset
        # django_get_or_create = ("name",)

    @classmethod
    def create(cls, **kwargs: Dict) -> Dataset:
        # ret = super().create(**kwargs)
        q: Query = cls.query.get_factory().create()
        q.run(persist=True)
        return q.datasets.first()


class FormatterFactory(DjangoModelFactory):
    name = factory.Sequence(lambda x: f"Formatter{x}")
    content_type = "html"

    class Meta:
        model = Formatter
        django_get_or_create = ("name",)


class ReportFactory(DjangoModelFactory):
    name = factory.Sequence(lambda x: f"Report{x}")
    query = factory.Iterator(Query.objects.all())
    formatter = factory.Iterator(Formatter.objects.all())
    owner = factory.SubFactory(UserFactory, is_superuser=True, is_staff=True, password="123")
    frequence = "mon,tue,wed,thu,fri,sat,sun"

    class Meta:
        model = Report
        django_get_or_create = ("name",)


class ParametrizerFactory(DjangoModelFactory):
    code = "active-business-areas"
    source = None

    class Meta:
        model = Parametrizer
        django_get_or_create = ("code",)


class ReportDocumentFactory(DjangoModelFactory):
    report = factory.SubFactory(ReportFactory)

    class Meta:
        model = ReportDocument

    @classmethod
    def create(cls, **kwargs: Dict) -> ReportDocument:
        fmt = Formatter.objects.get(name="Queryset To HTML")
        r: Report = ReportFactory(query=QueryFactory(), formatter=fmt)
        r.execute(run_query=True)
        return r.documents.first()


def get_group(name: str = "Group1", permissions: Optional[List[Permission]] = None) -> Group:
    group = GroupFactory(name)
    permission_names = permissions or []
    for permission_name in permission_names:
        try:
            app_label, codename = permission_name.split(".")
        except ValueError:
            raise ValueError(f"Invalid permission name `{permission_name}`")
    try:
        permission = Permission.objects.get(content_type__app_label=app_label, codename=codename)
    except Permission.DoesNotExist:
        raise Permission.DoesNotExist("Permission `{0}` does not exists", permission_name)

    group.permissions.add(permission)
    return group
