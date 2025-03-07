from typing import NoReturn, Type, TYPE_CHECKING

import pickle
from pathlib import Path

import pytest
from unittest.mock import Mock

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.manager import BaseManager

import factory
import fitz
import tablib
from docxtpl import DocxTemplate
from pypdf import PdfReader
from strategy_field.utils import fqn
from testutils.factories import DatasetFactory

from hope_country_report.apps.hope.models._inspect import Household
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
def data(user: NoReturn):
    from testutils.factories import CountryOfficeFactory, HouseholdFactory

    with state.set(must_tenant=False):
        co1: "CountryOffice" = CountryOfficeFactory(name="Afghanistan")

        HouseholdFactory(business_area=co1.business_area, withdrawn=False)
        HouseholdFactory(business_area=co1.business_area, withdrawn=False)
        HouseholdFactory(business_area=co1.business_area, withdrawn=False)


@pytest.fixture()
def query1(data: None):
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
def report(query1: NoReturn, formatter: NoReturn):
    from testutils.factories import ReportConfigurationFactory

    return ReportConfigurationFactory(formatters=[formatter], query=query1)


@pytest.fixture
def dataset(data: None, report: NoReturn, tmp_path: Path, households: BaseManager[Household]):
    return DatasetFactory(value=pickle.dumps(households))


@pytest.fixture
def updated_dataset(dataset, tmp_path):
    """
    Fixture to generate a dataset, add test images, and simulate missing fields.
    """

    data = [row for row in dataset.data.values()]
    test_image_path = tmp_path / "test_image.jpg"
    test_image_path.write_bytes(b"This is a test image")
    image_name = "test_image.jpg"

    saved_image_name = default_storage.save(image_name, ContentFile(b"This is a test image"))

    for row in data:
        row["head_of_household__photo"] = "non_existent_image.jpg"
        row["head_of_household__image"] = saved_image_name

    dataset.file.save("updated_dataset.pkl", ContentFile(dataset.marshall(data)))
    dataset.save()

    return dataset


def test_processor_process(dataset: NoReturn, tmp_path: Path, pp: "Type[ProcessorStrategy]"):
    from testutils.factories import FormatterFactory, ReportTemplateFactory

    extra = {}
    if pp.needs_file:
        tpl = Path(__file__).parent / f"template{pp.file_suffix}"
        extra = {"template": ReportTemplateFactory(doc=ContentFile(tpl.read_bytes(), name=tpl.name), name=tpl.name)}

    fmt = FormatterFactory(name=f"Test {pp.file_suffix}", **extra)
    out = pp(fmt).process({"dataset": dataset, "country_office": "Test"})
    assert isinstance(out, (bytearray, bytes)), f"{type(out)} is not bytes or bytearray"


def test_processor_html(dataset: NoReturn, tmp_path: Path):
    from testutils.factories import FormatterFactory

    fmt = FormatterFactory(name="Queryset To HTML")
    assert processors.ToHTML(fmt).process({"dataset": dataset})


def test_processor_xls(dataset: NoReturn, tmp_path: Path):
    result = processors.ToXLS(Mock()).process({"dataset": dataset})
    # Path("AAAA.xls").write_bytes(result)
    assert result


def test_processor_yml(dataset: NoReturn, tmp_path: Path):
    result = processors.ToYAML(Mock()).process({"dataset": dataset})
    # Path("AAAA.yml").write_text(result)
    assert result


def test_processor_json(dataset: NoReturn, tmp_path: Path):
    result = processors.ToJSON(Mock()).process({"dataset": dataset})
    # Path("AAAA.json").write_text(result)
    assert result


def test_processor_docx(dataset: NoReturn, tmp_path: Path):
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


def test_processor_pdf(dataset: NoReturn, tmp_path: Path):
    from testutils.factories import FormatterFactory

    code = FormatterFactory(name="Queryset To HTML").code
    fmt = FormatterFactory(name="aaa", code=code, processor=fqn(processors.ToPDF))

    result = processors.ToPDF(fmt).process({"dataset": dataset, "business_area": "Afghanistan"})
    output = tmp_path / "AAAA.pdf"
    output.write_bytes(result)
    PdfReader(output)
    assert result


def test_processor_pdfform(dataset: NoReturn, tmp_path: Path):
    from testutils.factories import ReportTemplateFactory

    tpl = ReportTemplateFactory(name="program_receipt.pdf")

    fmt = Mock()
    fmt.template = tpl
    result = processors.ToFormPDF(fmt).process({"dataset": dataset, "business_area": "Afghanistan"})
    output = tmp_path / "AAAA.pdf"
    output.write_bytes(result)
    PdfReader(output)
    assert result


def test_processor_pdf_with_image(updated_dataset: tablib.Dataset, tmp_path: Path):
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


def test_processor_pdf_with_missing_image(updated_dataset, tmp_path):
    """
    Test that the PDF processor can handle missing images gracefully.
    """
    from testutils.factories import ReportTemplateFactory

    # Generate PDF
    tpl = ReportTemplateFactory(
        name="program_receipt.pdf",
        doc=factory.LazyAttribute(
            lambda _: SimpleUploadedFile(
                "program_receipt.pdf",
                (Path(__file__).parent / "template.pdf").read_bytes(),
                content_type="application/pdf",
            )
        ),
    )
    fmt = Mock()
    fmt.template = tpl
    result = processors.ToFormPDF(fmt).process({"dataset": updated_dataset, "business_area": "Afghanistan"})

    # Assertions
    output = tmp_path / "WithMissingImage.pdf"
    assert result, "The PDF content is empty."
    output.write_bytes(result)
    assert output.exists(), "PDF file was not created."
    assert output.stat().st_size > 0, "PDF file is empty."

    # Verify placeholder for missing images
    with fitz.open(output) as document:
        for page in document:
            images = page.get_images(full=True)
            print(images)
            assert len(images) > 0, "No images found on the page; placeholders were not inserted."


def test_registry():
    assert registry.as_choices()
    assert not registry.as_choices(lambda x: False)
