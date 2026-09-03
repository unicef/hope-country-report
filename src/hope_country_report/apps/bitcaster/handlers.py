from typing import TYPE_CHECKING, Any

from django.dispatch import receiver

from hope_country_report.apps.bitcaster.client import trigger_event
from hope_country_report.signals import report_completed, report_failed

if TYPE_CHECKING:  # pragma: no cover
    from hope_country_report.apps.power_query.models import ReportConfiguration


@receiver(report_completed)
def handle_report_completed(sender: type, instance: "ReportConfiguration", **kwargs: Any) -> None:
    trigger_event(
        "report_completed",
        {
            "pk": instance.pk,
            "title": instance.title,
            "country_office": instance.country_office.slug if instance.country_office else None,
            "notify_to": [u.email for u in instance.notify_to.all()],
        },
    )


@receiver(report_failed)
def handle_report_failed(sender: type, instance: "ReportConfiguration", **kwargs: Any) -> None:
    trigger_event(
        "report_failed",
        {
            "pk": instance.pk,
            "title": instance.title,
            "country_office": instance.country_office.slug if instance.country_office else None,
            "error_message": instance.error_message,
        },
    )
