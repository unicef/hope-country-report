from typing import TYPE_CHECKING

from django.core.mail import EmailMessage, send_mail as django_send_mail

from constance import config

from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import User
    from hope_country_report.apps.power_query.models import ReportDocument


def send_mail(
    subject: str,
    message: str,
    from_email: str,
    recipient_list: list[str],
    fail_silently: bool = False,
    auth_user: str | None = None,
    auth_password: str | None = None,
    connection: str | None = None,
    html_message: str | None = None,
) -> int:
    if config.CATCH_ALL_EMAIL:
        recipient_list = [config.CATCH_ALL_EMAIL]
    return django_send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=fail_silently,
        auth_user=auth_user,
        auth_password=auth_password,
        connection=connection,
        html_message=html_message,
    )


def send_document_password(user: "User", document: "ReportDocument") -> int:
    if config.CATCH_ALL_EMAIL:
        recipient_list = [config.CATCH_ALL_EMAIL]
    else:
        recipient_list = [user.email]

    message = EmailMessage(to=recipient_list)
    message.template_id = config.ZIP_PASSWORD_MAILJET_TEMPLATE  # Mailjet numeric template id
    message.subject = "Document ready"
    message.from_email = None  # Use the From address stored with the template

    message.merge_global_data = {
        "document": {
            "name": document.title,
            "password": document.report.pwd,
            "file": document.file.name,
            "url": state.request.build_absolute_uri(document.get_absolute_url()),
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


#
#
# def send_mail_by_template(
#     subject,
#     message,
#     from_email,
#     recipient_list,
#     fail_silently=False,
#     auth_user=None,
#     auth_password=None,
#     connection=None,
#     html_message=None,
# ):
#     if config.CATCH_ALL_EMAIL:
#         recipient_list = [config.CATCH_ALL_EMAIL]
#     return django_send_mail(
#         subject=subject,
#         message=message,
#         from_email=from_email,
#         recipient_list=recipient_list,
#         fail_silently=fail_silently,
#         auth_user=auth_user,
#         auth_password=auth_password,
#         connection=connection,
#         html_message=html_message,
#     )
