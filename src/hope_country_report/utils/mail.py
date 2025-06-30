from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage

from constance import config
from sentry_sdk import capture_exception

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import User
    from hope_country_report.apps.power_query.models import ReportConfiguration, ReportDocument
    from hope_country_report.types.http import AuthHttpRequest


def send_document_password(user: "User", document: "ReportDocument", request: "AuthHttpRequest | None" = None) -> int:
    if config.CATCH_ALL_EMAIL:
        recipient_list = [config.CATCH_ALL_EMAIL]
    else:
        recipient_list = [user.email]
    if not recipient_list:
        return 0
    url = document.get_absolute_url()
    if request:
        url = request.build_absolute_uri(url)
    else:
        try:
            domain = Site.objects.get_current().domain
            scheme = "https" if not settings.DEBUG else "http"
            url = f"{scheme}://{domain}{url}"
        except Exception as e:
            capture_exception(e)

    message = EmailMessage(to=recipient_list, from_email=settings.DEFAULT_FROM_EMAIL)

    message.template_id = config.MAILJET_TEMPLATE_REPORT_READY  # Mailjet numeric template id
    message.subject = f"Your password for {document.title}"

    message.merge_global_data = {
        "document": {
            "name": document.title,
            "password": document.report.pwd,
            "file": document.file.name,
            "url": url,
        },
        "user": {
            "name": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "friendly_name": user.friendly_name,
            "username": user.username,
        },
    }
    return message.send()


def send_request_access(
    sender: "User", report: "ReportConfiguration", message: str = "", request: "AuthHttpRequest | None" = None
) -> int:
    url = report.get_absolute_url()
    if request:
        url = request.build_absolute_uri(url)
    else:
        try:
            domain = Site.objects.get_current().domain
            scheme = "https" if not settings.DEBUG else "http"
            url = f"{scheme}://{domain}{url}"
        except Exception as e:
            capture_exception(e)

    if config.CATCH_ALL_EMAIL:
        recipient_list = [config.CATCH_ALL_EMAIL]
    else:
        recipient_list = [report.owner.email]

    email = EmailMessage(
        to=recipient_list,
        from_email=settings.DEFAULT_FROM_EMAIL,
        subject=f"{sender.full_name} wants to access '{report.title}'",
        body=f"""

Requested by: {sender.full_name} - {sender.email}
Requesting access to: {report.title}

{message}

""",
    )

    email.merge_global_data = {
        "report": {
            "title": report.title,
            "url": url,
        },
    }
    return email.send()


def notify_report_completion(report: "ReportConfiguration", request: "AuthHttpRequest | None" = None) -> int:
    url = report.get_absolute_url()
    docs_url = report.get_documents_url()

    if request:
        url = request.build_absolute_uri(url)
        docs_url = request.build_absolute_uri(docs_url)
    else:
        try:
            domain = Site.objects.get_current().domain
            scheme = "https" if not settings.DEBUG else "http"
            url = f"{scheme}://{domain}{url}"
            docs_url = f"{scheme}://{domain}{docs_url}"
        except Exception as e:
            capture_exception(e)

    if config.CATCH_ALL_EMAIL:
        recipient_list = [config.CATCH_ALL_EMAIL]
    else:
        recipient_list = [u.email for u in report.notify_to.all()]

    if not recipient_list:
        return 0

    message = EmailMessage(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
        bcc=recipient_list,
        subject="Report updated/created",
        body=f"""Dear User,

Report {report.title} has been successfully updated/created.

You can view/download produced documents at {docs_url}


Kind regards,

The HOPE Team
""",
    )

    message.merge_global_data = {
        "report": {
            "title": report.title,
            "url": url,
            "documents_url": docs_url,
        },
    }
    return message.send()
