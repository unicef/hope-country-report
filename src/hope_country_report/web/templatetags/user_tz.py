import datetime

from django.template import Library
from django.template.defaultfilters import date
from django.utils import timezone

from hope_country_report.apps.core.models import User
from hope_country_report.state import state

register = Library()


@register.filter(expects_localtime=True, is_safe=False)
def userdatetime(value: datetime.datetime | None, fmt: str | None = None) -> str:
    if not value:
        return ""
    if state.request:
        user: User = state.request.user
        if user and user.is_authenticated and user.timezone:
            tz = user.timezone
            value = value.astimezone(tz)
            if fmt is None:
                fmt = "Y M d h:i a"
            if fmt in ["time", "t"]:
                fmt = user.time_format
            elif fmt in ["date", "d"]:
                fmt = user.date_format
            elif fmt == "-":
                today = timezone.now().date()
                if value.date() == today:
                    fmt = user.time_format
    if not fmt:
        fmt = "Y M d h:i a"

    return date(value, fmt)
