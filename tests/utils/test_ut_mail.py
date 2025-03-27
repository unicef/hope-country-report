import pytest
from unittest.mock import Mock

from constance.test import override_config

from hope_country_report.state import state
from hope_country_report.utils.mail import notify_report_completion, send_document_password, send_request_access

USER_EMAIL = "user@example.com"


@pytest.fixture
def report():
    from testutils.factories import ReportConfigurationFactory, UserFactory

    return ReportConfigurationFactory(owner=UserFactory(email=USER_EMAIL))


@pytest.fixture
def report_document(report):
    from testutils.factories import ReportDocumentFactory

    return ReportDocumentFactory(report=report)


@pytest.mark.parametrize(
    "config,expected",
    [
        ({"request": None, "CATCH_ALL_EMAIL": None}, USER_EMAIL),
        ({"request": None, "CATCH_ALL_EMAIL": "test@example.com"}, "test@example.com"),
        ({"request": Mock(), "CATCH_ALL_EMAIL": "test@example.com"}, "test@example.com"),
    ],
)
def test_send_request_access(config, expected, mocked_responses, user, report, mailoutbox):
    with override_config(CATCH_ALL_EMAIL=config["CATCH_ALL_EMAIL"]):
        with state.set(request=config["request"]):
            res = send_request_access(user, report)
            assert res == 1
            assert len(mailoutbox) == 1
            assert mailoutbox[0].to == [expected]


@pytest.mark.parametrize(
    "config,expected",
    [
        ({"request": None, "CATCH_ALL_EMAIL": None}, USER_EMAIL),
        ({"request": None, "CATCH_ALL_EMAIL": "test@example.com"}, "test@example.com"),
        ({"request": Mock(), "CATCH_ALL_EMAIL": "test@example.com"}, "test@example.com"),
    ],
)
def test_send_document_password(config, expected, mocked_responses, user, report_document, mailoutbox):
    with override_config(CATCH_ALL_EMAIL=config["CATCH_ALL_EMAIL"]):
        with state.set(request=config["request"]):
            res = send_document_password(report_document.report.owner, report_document)
            assert res == 1
            assert len(mailoutbox) == 1
            assert mailoutbox[0].to == [expected]


@pytest.mark.parametrize(
    "config,expected",
    [
        ({"request": None, "CATCH_ALL_EMAIL": None}, USER_EMAIL),
        ({"request": None, "CATCH_ALL_EMAIL": "test@example.com"}, "test@example.com"),
        ({"request": Mock(), "CATCH_ALL_EMAIL": "test@example.com"}, "test@example.com"),
    ],
)
def test_notify_report_completion(config, expected, mocked_responses, user, report, mailoutbox):
    report.notify_to.add(report.owner)
    with override_config(CATCH_ALL_EMAIL=config["CATCH_ALL_EMAIL"]):
        with state.set(request=config["request"]):
            res = notify_report_completion(report)
            assert res == 1
            assert len(mailoutbox) == 1
            assert mailoutbox[0].to == [expected]


def test_notify_report_completion_no_recipients(mocked_responses, report, mailoutbox):
    res = notify_report_completion(report)
    assert res == 0
