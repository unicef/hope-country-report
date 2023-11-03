import datetime

from django.contrib.auth.models import AnonymousUser
from django.template import Library
from django.template.defaultfilters import date
from django.utils import timezone

from hope_country_report.apps.core.models import User
from hope_country_report.state import state

register = Library()


def get_format_for_user(user: User | AnonymousUser, value: datetime.datetime, fmt: str | None) -> str | None:
    datetime_format = getattr(user, "datetime_format", "Y M d h:i a")
    time_format = getattr(user, "time_format", "h:i a")
    date_format = getattr(user, "date_format", "Y M d")
    if fmt in ["full", "dt"]:
        fmt = datetime_format
    elif fmt in ["time", "t"]:
        fmt = time_format
    elif fmt in ["date", "d"]:
        fmt = date_format
    elif fmt in ["-"]:
        today = timezone.now().date()
        if value.date() == today:
            fmt = time_format
        else:
            fmt = date_format
    return fmt


@register.filter(expects_localtime=True, is_safe=False)
def userdatetime(value: datetime.datetime | None, fmt: str | None = None) -> str:
    if not value:
        return ""

    if state.request:
        user = state.request.user or AnonymousUser()
    else:
        user = AnonymousUser()
    if user.is_authenticated and user.timezone:
        tz = user.timezone
        value = value.astimezone(tz)
    fmt = get_format_for_user(user, value, fmt)

    if not fmt:
        fmt = "Y M d h:i a"

    return date(value, fmt)
