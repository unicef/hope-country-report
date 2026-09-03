import pytest
from unittest.mock import patch

from hope_country_report.apps.power_query.models import ReportConfiguration
from hope_country_report.signals import report_completed, report_failed

pytestmark = pytest.mark.django_db


@pytest.fixture()
def report(db):
    from testutils.factories import ReportConfigurationFactory

    return ReportConfigurationFactory.create()


@pytest.fixture()
def failed_report(report):
    report.error_message = "Query timed out"
    return report


def test_handle_report_completed_calls_trigger_event(report):
    with patch("hope_country_report.apps.bitcaster.handlers.trigger_event") as mock_trigger:
        report_completed.send(sender=ReportConfiguration, instance=report)

    mock_trigger.assert_called_once_with(
        "report_completed",
        {
            "pk": report.pk,
            "title": report.title,
            "country_office": report.country_office.slug,
            "notify_to": [],
        },
    )


def test_handle_report_failed_calls_trigger_event(failed_report):
    with patch("hope_country_report.apps.bitcaster.handlers.trigger_event") as mock_trigger:
        report_failed.send(sender=ReportConfiguration, instance=failed_report)

    mock_trigger.assert_called_once_with(
        "report_failed",
        {
            "pk": failed_report.pk,
            "title": failed_report.title,
            "country_office": failed_report.country_office.slug,
            "error_message": "Query timed out",
        },
    )
