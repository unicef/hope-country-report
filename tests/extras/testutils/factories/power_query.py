from typing import TYPE_CHECKING

from django.core.files.base import ContentFile

import factory
from strategy_field.utils import fqn

from hope_country_report.apps.power_query.models import (
    Dataset,
    Formatter,
    Parametrizer,
    Query,
    ReportConfiguration,
    ReportDocument,
    ReportTemplate,
)
from hope_country_report.apps.power_query.processors import ToHTML

from .base import AutoRegisterModelFactory
from .contenttypes import ContentTypeFactory
from .user import CountryOfficeFactory, UserFactory

if TYPE_CHECKING:
    from typing import Dict


class QueryFactory(AutoRegisterModelFactory):
    name = factory.Sequence(lambda n: "Query %s" % n)
    owner = factory.SubFactory(UserFactory)
    country_office = factory.SubFactory(CountryOfficeFactory)
    target = factory.SubFactory(ContentTypeFactory, app_label="hope", model="household")
    code = "result=conn.all()"
    parent = None
    active = True
    curr_async_result_id = None
    last_async_result_id = None

    class Meta:
        model = Query
        django_get_or_create = ("name",)


class ReportTemplateFactory(AutoRegisterModelFactory):
    name = factory.Sequence(lambda n: "ReportTemplate %s" % n)

    class Meta:
        model = ReportTemplate
        django_get_or_create = ("name",)


class FormatterFactory(AutoRegisterModelFactory):
    name = "Queryset To HTML"
    template = None
    processor = fqn(ToHTML)

    class Meta:
        model = Formatter
        django_get_or_create = ("name",)


class DatasetFactory(AutoRegisterModelFactory):
    query = factory.SubFactory(QueryFactory)

    class Meta:
        model = Dataset

    @classmethod
    def create(cls, **kwargs: "Dict") -> Dataset:
        q: Query = cls.query.get_factory().create()
        q.run(persist=True)
        return q.datasets.first()


class ReportConfigurationFactory(AutoRegisterModelFactory):
    name = factory.Sequence(lambda n: "Report %s" % n)
    title = factory.Sequence(lambda n: "Report %s" % n)
    query = factory.SubFactory(QueryFactory)
    owner = factory.SubFactory(UserFactory)
    country_office = factory.SubFactory(CountryOfficeFactory)
    compress = False

    class Meta:
        model = ReportConfiguration
        django_get_or_create = ("name",)

    @factory.post_generation
    def formatters(self, create, formatters, **kwargs):
        from hope_country_report.apps.power_query.defaults import create_defaults

        if not create:
            # Simple build, do nothing.
            return

        if formatters:
            # A list of groups were passed in, use them
            for formatter in formatters:
                self.formatters.add(formatter)
        else:
            create_defaults()
            fmt = Formatter.objects.get(name="Queryset To HTML")
            self.formatters.add(fmt)
        self.execute(run_query=True, notify=False)


class ReportDocumentFactory(AutoRegisterModelFactory):
    report = factory.SubFactory(ReportConfigurationFactory)
    dataset = factory.SubFactory(DatasetFactory)
    formatter = factory.SubFactory(FormatterFactory)

    class Meta:
        model = ReportDocument

    @classmethod
    def create(cls, **kwargs: "Dict") -> ReportDocument:
        ret = super().create(**kwargs)
        ret.file = ContentFile("", f"test{ret.formatter.file_suffix}")
        ret.save()
        return ret


class ParametrizerFactory(AutoRegisterModelFactory):
    code = factory.Sequence(lambda n: "params-%s" % n)
    source = None

    class Meta:
        model = Parametrizer
        django_get_or_create = ("code",)
