from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest
from constance.test import override_config

from hope_country_report.state import state
from hope_country_report.utils.mail import notify_report_completion, send_document_password, send_request_access

if TYPE_CHECKING:
    from hope_country_report.apps.power_query.models import ReportConfiguration, ReportDocument


USER_EMAIL = "user@example.com"


@pytest.fixture()
def report() -> "ReportConfiguration":
    from testutils.factories import ReportConfigurationFactory, UserFactory

    return ReportConfigurationFactory(owner=UserFactory(email=USER_EMAIL))


@pytest.fixture()
def report_document(report):
    from testutils.factories import ReportDocumentFactory

    return ReportDocumentFactory(report=report)


@pytest.mark.parametrize(
    "cfg,expected",
    [
        ({"request": None, "CATCH_ALL_EMAIL": None}, USER_EMAIL),
        ({"request": None, "CATCH_ALL_EMAIL": "test@example.com"}, "test@example.com"),
        ({"request": Mock(), "CATCH_ALL_EMAIL": "test@example.com"}, "test@example.com"),
    ],
)
def test_send_request_access(cfg, expected, mocked_responses, user, report, mailoutbox):
    with override_config(CATCH_ALL_EMAIL=cfg["CATCH_ALL_EMAIL"]):
        with state.set(request=cfg["request"]):
            res = send_request_access(user, report)
            assert res == 1
            assert len(mailoutbox) == 1
            assert mailoutbox[0].bcc == [expected]


@pytest.mark.parametrize(
    "cfg,expected",
    [
        ({"request": None, "CATCH_ALL_EMAIL": None}, USER_EMAIL),
        ({"request": None, "CATCH_ALL_EMAIL": "test@example.com"}, "test@example.com"),
        ({"request": Mock(), "CATCH_ALL_EMAIL": "test@example.com"}, "test@example.com"),
    ],
)
def test_send_document_password(cfg, expected, mocked_responses, user, report_document: "ReportDocument", mailoutbox):
    with override_config(CATCH_ALL_EMAIL=cfg["CATCH_ALL_EMAIL"]):
        with state.set(request=cfg["request"]):
            res = send_document_password(report_document.report.owner, report_document.report)
            assert res == 1
            assert len(mailoutbox) == 1
            assert mailoutbox[0].to == [expected]


@pytest.mark.parametrize(
    "cfg,expected",
    [
        ({"request": None, "CATCH_ALL_EMAIL": None}, USER_EMAIL),
        ({"request": None, "CATCH_ALL_EMAIL": "test@example.com"}, "test@example.com"),
        ({"request": Mock(), "CATCH_ALL_EMAIL": "test@example.com"}, "test@example.com"),
    ],
)
def test_notify_report_completion(cfg, expected, mocked_responses, user, report: "ReportConfiguration", mailoutbox):
    report.notify_to.add(report.owner)
    with override_config(CATCH_ALL_EMAIL=cfg["CATCH_ALL_EMAIL"]):
        with state.set(request=cfg["request"]):
            res = notify_report_completion(report)
            assert res == 1
            assert len(mailoutbox) == 1
            assert mailoutbox[0].bcc == [expected]


def test_notify_report_completion_no_recipients(mocked_responses, report, mailoutbox):
    with override_config(CATCH_ALL_EMAIL=[]):
        res = notify_report_completion(report)
        assert res == 0
