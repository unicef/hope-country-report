from typing import TYPE_CHECKING

from django.apps import apps
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile

import factory
from strategy_field.utils import fqn

from hope_country_report.apps.power_query.models import (
    ChartPage,
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
    name = factory.Sequence(lambda n: f"Query {n}")
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
    name = factory.Sequence(lambda n: f"ReportTemplate {n}")

    class Meta:
        model = ReportTemplate
        django_get_or_create = ("name",)

    country_office = factory.SubFactory(CountryOfficeFactory)
    name = factory.Faker("word")
    file_suffix = ".pdf"
    doc = factory.LazyAttribute(
        lambda _: SimpleUploadedFile("test_template.pdf", b"Test file content", content_type="application/pdf")
    )


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
        # q: Query = cls.query.get_factory().create()
        q: Query = QueryFactory()
        assert q.target.app_label
        assert q.target.model
        assert apps.get_model(q.target.app_label, q.target.model)
        assert q.target.model_class()
        q.run(persist=True)
        return q.datasets.first()


class ReportConfigurationFactory(AutoRegisterModelFactory):
    name = factory.Sequence(lambda n: f"Report {n}")
    title = factory.Sequence(lambda n: f"Report {n}")
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
    code = factory.Sequence(lambda n: f"params-{n}")
    source = None

    class Meta:
        model = Parametrizer
        django_get_or_create = ("code",)


class ChartPageFactory(AutoRegisterModelFactory):
    country_office = factory.SubFactory(CountryOfficeFactory)
    title = factory.Sequence(lambda n: f"ChartPage {n}")
    query = factory.SubFactory(QueryFactory, country_office=factory.SelfAttribute("..country_office"))

    class Meta:
        model = ChartPage
        django_get_or_create = ("title",)
