from datetime import datetime

from django.template import Library
from django.template.defaultfilters import date

from hope_country_report.apps.core.models import User

register = Library()


@register.filter(expects_localtime=True, is_safe=False)
def userdatetime(value: datetime, user: "User|None" = None, arg: str = "Y M d H:i") -> str:
    if user:
        try:
            tz = user.timezone
            value = value.astimezone(tz)
        except ValueError:
            pass
    return date(value, arg)


@register.filter(expects_localtime=True, is_safe=False)
def usertime(value: datetime, user: "User|None" = None, arg: str = "H:i") -> str:
    if user:
        try:
            tz = user.timezone
            value = value.astimezone(tz)
        except ValueError:
            pass
    return date(value, arg)
