import factory
from power_query.models import Dataset, Formatter, Query, Report, ReportDocument

from . import ContentTypeFactory
from .base import AutoRegisterModelFactory
from .user import UserFactory


class QueryFactory(AutoRegisterModelFactory):
    name = factory.Sequence(lambda n: "Query %s" % n)
    owner = factory.SubFactory(UserFactory)
    target = factory.SubFactory(ContentTypeFactory)

    class Meta:
        model = Query


class FormatterFactory(AutoRegisterModelFactory):
    class Meta:
        model = Formatter


class DatasetFactory(AutoRegisterModelFactory):
    query = factory.SubFactory(QueryFactory)
    value = b""

    class Meta:
        model = Dataset


class ReportFactory(AutoRegisterModelFactory):
    query = factory.SubFactory(QueryFactory)
    formatter = factory.SubFactory(FormatterFactory)

    class Meta:
        model = Report


class ReportDocumentFactory(AutoRegisterModelFactory):
    report = factory.SubFactory(ReportFactory)
    dataset = factory.SubFactory(DatasetFactory)

    class Meta:
        model = ReportDocument
