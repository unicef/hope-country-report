from typing import TYPE_CHECKING

from pathlib import Path, PurePath
from tempfile import TemporaryDirectory

import pytest
from unittest import mock
from unittest.mock import Mock

from django.conf import settings

import pyzipper
from constance.test import override_config
from extras.testutils.factories import ReportConfigurationFactory

from hope_country_report.apps.power_query.models import ReportConfiguration
from hope_country_report.config.celery import app
from hope_country_report.state import state
from hope_country_report.utils.os import pushd

if TYPE_CHECKING:
    from typing import TypedDict

    from hope_country_report.apps.core.models import CountryOffice, User
    from hope_country_report.apps.hope.models import Household
    from hope_country_report.apps.power_query.models import Query, ReportDocument

    class _DATA(TypedDict):
        user: User
        co1: CountryOffice
        co2: CountryOffice
        hh1: tuple[Household, Household]
        hh2: tuple[Household, Household]


@pytest.fixture()
def data(reporters) -> "_DATA":
    from testutils.factories import CountryOfficeFactory, HouseholdFactory, UserFactory, UserRoleFactory

    with state.set(must_tenant=False):
        co1: "CountryOffice" = CountryOfficeFactory(name="Afghanistan")
        co2: "CountryOffice" = CountryOfficeFactory(name="Niger")

        h11: "Household" = HouseholdFactory(unicef_id="u1", business_area=co1.business_area, withdrawn=True)
        h12: "Household" = HouseholdFactory(unicef_id="u2", business_area=co1.business_area, withdrawn=False)
        h21: "Household" = HouseholdFactory(unicef_id="u3", business_area=co2.business_area, withdrawn=True)
        h22: "Household" = HouseholdFactory(unicef_id="u4", business_area=co2.business_area, withdrawn=False)

        user = UserFactory(username="user", is_staff=False, is_superuser=False, is_active=True)
        UserRoleFactory(country_office=co1, group=reporters, user=user)

    return {"co1": co1, "co2": co2, "hh1": (h11, h12), "hh2": (h21, h22), "user": user}


@pytest.fixture()
def query(data: "_DATA"):
    from testutils.factories import ContentTypeFactory, QueryFactory

    return QueryFactory(
        target=ContentTypeFactory(app_label="hope", model="household"),
        name="Query",
        code="result=conn.all()",
    )


@pytest.fixture()
def query_impl(data: "_DATA", query):
    from testutils.factories import QueryFactory

    return QueryFactory(
        target=None,
        name="Query Implement",
        parent=query,
        country_office=data["co1"],
        code=None,
    )


@pytest.fixture()
def query2(afg_user):
    from testutils.factories import Query, QueryFactory

    Query.objects.filter(name="Debug Query").delete()
    q = QueryFactory(
        owner=afg_user,
        name="Debug Query",
        curr_async_result_id=None,
        code="""result=[1,2,3,4]""",
    )
    yield q
    if q.curr_async_result_id:
        with app.pool.acquire(block=True) as conn:
            conn.default_channel.client.srem(settings.CELERY_TASK_REVOKED_QUEUE, q.curr_async_result_id)


@pytest.fixture()
def report(query2: "Query", monkeypatch):
    from testutils.factories import ReportConfigurationFactory

    with mock.patch("hope_country_report.apps.power_query.models.report.notify_report_completion", Mock()):
        return ReportConfigurationFactory(name="Celery Report", query=query2, owner=query2.owner)


def test_celery_no_worker(db, settings, report: "ReportConfiguration") -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = False
    assert report.status == "Not scheduled"
    report.queue()
    assert report.status == "QUEUED"
    report.terminate()
    assert report.status == "CANCELED"


def test_report_refresh(db, settings, report: "ReportConfiguration") -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    report.execute(True)
    assert report.documents.exists()
    doc = report.documents.first()
    assert doc.file
    report.execute(False)
    assert doc.file


@override_config(CATCH_ALL_EMAIL="")
def test_report_zip(db, settings, report: "ReportConfiguration", mailoutbox) -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    report.compress = True
    assert report.owner
    assert report.owner.email

    report.execute(True)
    assert report.documents.exists()

    doc: "ReportDocument" = report.documents.first()
    assert doc.file
    assert doc.content_type == "application/x-zip-compressed"

    # Use pyzipper to read the AES-encrypted ZIP file
    with pyzipper.AESZipFile(doc.file.path, "r") as archive:
        assert len(archive.namelist()) == 1
        page_document = archive.open(archive.namelist()[0])
        assert PurePath(page_document.name).suffix == doc.formatter.file_suffix


@override_config(CATCH_ALL_EMAIL="")
def test_report_zip_protected_notify_email(
    transactional_db, rf, settings, report: "ReportConfiguration", mailoutbox
) -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    report.compress = True
    report.protect = True
    request = rf.get("/")
    request.user = report.owner

    with state.set(request=request, must_tenant=False):
        report.execute(True)

    assert len(mailoutbox) == 1, [m.to for m in mailoutbox]
    assert [m.to for m in mailoutbox] == [[report.owner.email]]
    assert mailoutbox[0].subject == f"Your password for {report.title}"


@override_config(CATCH_ALL_EMAIL="")
def test_report_zip_protected(transactional_db, rf, settings, report: "ReportConfiguration", mailoutbox) -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    report.compress = True
    report.protect = True
    request = rf.get("/")
    request.user = report.owner
    assert not report.pwd
    with state.set(request=request, must_tenant=False):
        report.execute(True)

    assert report.pwd

    doc: "ReportDocument" = report.documents.first()
    assert doc.file
    assert doc.content_type == "application/x-zip-compressed"

    with pyzipper.AESZipFile(doc.file.path, "r") as archive:
        with pytest.raises(RuntimeError):
            archive.open(archive.namelist()[0])

        archive.setpassword(report.pwd.encode("utf-8"))
        assert len(archive.namelist()) == 1
        filename = archive.namelist()[0]

        assert not filename.endswith("/")

        with TemporaryDirectory(prefix="~") as tdir:
            with pushd(tdir):
                archive.extract(filename, tdir)
                extracted_file = Path(tdir) / filename

                assert extracted_file.exists()
                assert extracted_file.is_file()
                extracted_content = extracted_file.read_bytes()
                dataset = doc.dataset
                formatter = doc.formatter
                context = {
                    **dataset.arguments,
                    **dataset.extra,
                    **report.context,
                }
                args_desc = "_".join([str(value) for value in dataset.arguments.values()])
                try:
                    title = f"{report.title.format(**context)}{args_desc}".title()
                except KeyError:
                    title = report.title
                rendered_content = formatter.render(
                    {
                        "dataset": dataset,
                        "report": report,
                        "title": title,
                        "context": context,
                    }
                )
                if isinstance(rendered_content, bytearray):
                    expected_content = bytes(rendered_content)
                else:
                    expected_content = rendered_content.encode("utf-8")

                assert extracted_content == expected_content


def test_report_abstract(db, query_impl: "Query") -> None:
    with mock.patch("hope_country_report.apps.power_query.models.report.notify_report_completion", Mock()):
        rep = ReportConfigurationFactory(name="Test Report", query=query_impl.parent, owner=query_impl.owner)
    assert query_impl.parent.abstract
    assert ReportConfiguration.objects.filter(parent=rep, query=query_impl).exists()
