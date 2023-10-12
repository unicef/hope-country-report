from typing import TYPE_CHECKING

import factory

from hope_country_report.apps.power_query.models import Dataset, Formatter, Parametrizer, Query, Report, ReportDocument

from .base import AutoRegisterModelFactory
from .contenttypes import ContentTypeFactory
from .user import UserFactory

if TYPE_CHECKING:
    from typing import Dict


class QueryFactory(AutoRegisterModelFactory):
    name = factory.Sequence(lambda n: "Query %s" % n)
    owner = factory.SubFactory(UserFactory)
    target = factory.SubFactory(ContentTypeFactory, app_label="hope", model="household")
    code = "result=conn.all()"
    parent = None
    active = True

    class Meta:
        model = Query


class FormatterFactory(AutoRegisterModelFactory):
    name = "Queryset To HTML"

    class Meta:
        model = Formatter
        django_get_or_create = ("name",)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        from hope_country_report.apps.power_query.defaults import create_defaults

        create_defaults()
        return super()._create(model_class, *args, **kwargs)


class DatasetFactory(AutoRegisterModelFactory):
    query = factory.SubFactory(QueryFactory)
    value = b""

    class Meta:
        model = Dataset

    @classmethod
    def create(cls, **kwargs: "Dict") -> Dataset:
        # ret = super().create(**kwargs)
        q: Query = cls.query.get_factory().create()
        q.run(persist=True)
        return q.datasets.first()


class ReportFactory(AutoRegisterModelFactory):
    name = factory.Sequence(lambda n: "Report %s" % n)
    query = factory.SubFactory(QueryFactory)
    formatter = factory.SubFactory(FormatterFactory)
    owner = factory.SubFactory(UserFactory, is_superuser=True, is_staff=True, password="123")
    frequence = "mon,tue,wed,thu,fri,sat,sun"

    class Meta:
        model = Report
        django_get_or_create = ("name",)


class ReportDocumentFactory(AutoRegisterModelFactory):
    report = factory.SubFactory(ReportFactory)

    class Meta:
        model = ReportDocument

    @classmethod
    def create(cls, **kwargs: "Dict") -> ReportDocument:
        from hope_country_report.apps.power_query.defaults import create_defaults

        create_defaults()
        fmt = Formatter.objects.get(name="Queryset To HTML")
        r: Report = ReportFactory(query=QueryFactory(), formatter=fmt)
        r.execute(run_query=True)
        return r.documents.first()


class ParametrizerFactory(AutoRegisterModelFactory):
    code = "active-business-areas"
    source = None

    class Meta:
        model = Parametrizer
        django_get_or_create = ("code",)
