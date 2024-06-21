from typing import Type, TYPE_CHECKING

import pickle
from pathlib import Path

import pytest
from unittest.mock import Mock

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from docxtpl import DocxTemplate
from pypdf import PdfReader
from strategy_field.utils import fqn
from testutils.factories import DatasetFactory

from hope_country_report.apps.power_query import processors
from hope_country_report.apps.power_query.processors import ProcessorStrategy, registry
from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice


def pytest_generate_tests(metafunc):
    if "pp" in metafunc.fixturenames:
        m = [p for p in registry]
        ids = [f"{p.__name__}|{p.file_suffix}" for p in registry]
        metafunc.parametrize("pp", m, ids=ids)


@pytest.fixture()
def data(user):
    from testutils.factories import CountryOfficeFactory, HouseholdFactory

    with state.set(must_tenant=False):
        co1: "CountryOffice" = CountryOfficeFactory(name="Afghanistan")

        HouseholdFactory(business_area=co1.business_area, withdrawn=False)
        HouseholdFactory(business_area=co1.business_area, withdrawn=False)
        HouseholdFactory(business_area=co1.business_area, withdrawn=False)


@pytest.fixture()
def query1(data):
    from testutils.factories import ContentTypeFactory, QueryFactory

    return QueryFactory(
        target=ContentTypeFactory(app_label="hope", model="household"),
        name="Query1",
        code="result=conn.all()",
    )


@pytest.fixture()
def formatter():
    from testutils.factories import FormatterFactory

    return FormatterFactory(name="Queryset To HTML")


@pytest.fixture()
def report(query1, formatter):
    from testutils.factories import ReportConfigurationFactory

    return ReportConfigurationFactory(formatters=[formatter], query=query1)


@pytest.fixture
def dataset(data, report, tmp_path, households):

    return DatasetFactory(value=pickle.dumps(households))


@pytest.fixture
def updated_dataset(households, report, tmp_path):
    household = households.first()
    if not household or not household.head_of_household:
        raise ValueError("No Household objects found with a related HeadOfHousehold in the database.")
    test_image_path = tmp_path / "test_image.jpg"
    test_image_path.write_bytes(b"This is a test image")
    image_name = "test_images/test_image.jpg"
    with open(str(test_image_path), "rb") as test_image:
        image_file = ContentFile(test_image.read(), name=image_name)
        saved_image_name = default_storage.save(image_name, image_file)
    head_of_household = household.head_of_household
    head_of_household.photo = saved_image_name
    head_of_household.save()
    return DatasetFactory(value=pickle.dumps(households.values("unicef_id", "head_of_household__photo")))


def test_processor_process(dataset, tmp_path, pp: "Type[ProcessorStrategy]"):
    from testutils.factories import FormatterFactory, ReportTemplateFactory

    extra = {}
    if pp.needs_file:
        tpl = Path(__file__).parent / f"template{pp.file_suffix}"
        extra = {"template": ReportTemplateFactory(doc=ContentFile(tpl.read_bytes(), name=tpl.name), name=tpl.name)}

    fmt = FormatterFactory(name=f"Test {pp.file_suffix}", **extra)
    out = pp(fmt).process({"dataset": dataset, "country_office": "Test"})
    assert isinstance(out, (bytearray, bytes)), f"{type(out)} is not bytes or bytearray"


def test_processor_html(dataset, tmp_path):
    from testutils.factories import FormatterFactory

    fmt = FormatterFactory(name="Queryset To HTML")
    assert processors.ToHTML(fmt).process({"dataset": dataset})


def test_processor_xls(dataset, tmp_path):
    result = processors.ToXLS(Mock()).process({"dataset": dataset})
    # Path("AAAA.xls").write_bytes(result)
    assert result


def test_processor_yml(dataset, tmp_path):
    result = processors.ToYAML(Mock()).process({"dataset": dataset})
    # Path("AAAA.yml").write_text(result)
    assert result


def test_processor_json(dataset, tmp_path):
    result = processors.ToJSON(Mock()).process({"dataset": dataset})
    # Path("AAAA.json").write_text(result)
    assert result


def test_processor_docx(dataset, tmp_path):
    from testutils.factories import ReportTemplateFactory

    tpl = ReportTemplateFactory(name="households.docx")

    fmt = Mock()
    fmt.template = tpl

    result = processors.ToWord(fmt).process({"dataset": dataset, "business_area": "Afghanistan", "country_office": ""})
    # try ti save and open
    output = tmp_path / "AAAA.docx"
    output.write_bytes(result)
    DocxTemplate(output)
    assert result


def test_processor_pdf(dataset, tmp_path):
    from testutils.factories import FormatterFactory

    code = FormatterFactory(name="Queryset To HTML").code
    fmt = FormatterFactory(name="aaa", code=code, processor=fqn(processors.ToPDF))

    result = processors.ToPDF(fmt).process({"dataset": dataset, "business_area": "Afghanistan"})
    output = tmp_path / "AAAA.pdf"
    output.write_bytes(result)
    PdfReader(output)
    assert result


def test_processor_pdfform(dataset, tmp_path):
    from testutils.factories import ReportTemplateFactory

    tpl = ReportTemplateFactory(name="program_receipt.pdf")

    fmt = Mock()
    fmt.template = tpl
    result = processors.ToFormPDF(fmt).process({"dataset": dataset, "business_area": "Afghanistan"})
    output = tmp_path / "AAAA.pdf"
    output.write_bytes(result)
    PdfReader(output)
    assert result


def test_processor_pdf_with_image(updated_dataset, tmp_path):
    from testutils.factories import ReportTemplateFactory

    tpl = ReportTemplateFactory(name="program_receipt.pdf")
    fmt = Mock()
    fmt.template = tpl
    result = processors.ToFormPDF(fmt).process({"dataset": updated_dataset, "business_area": "Afghanistan"})
    output = tmp_path / "WithImage.pdf"
    assert result, "The PDF content is empty."
    output.write_bytes(result)
    assert output.exists(), "PDF file was not created."
    assert output.stat().st_size > 0, "PDF file is empty."

    pdf = PdfReader(output)
    assert pdf, "Failed to read the generated PDF file."


def test_registry():
    assert registry.as_choices()
    assert not registry.as_choices(lambda x: False)
