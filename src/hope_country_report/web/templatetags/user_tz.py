from datetime import datetime

from django.contrib.auth.models import AnonymousUser
from django.template import Library
from django.template.defaultfilters import date

from hope_country_report.apps.core.models import User
from hope_country_report.state import state

register = Library()


@register.filter(expects_localtime=True, is_safe=False)
def userdatetime(value: datetime | None, user: "User|AnonymousUser|None" = None, arg: str = "Y M d H:i") -> str:
    if not value:
        return ""
    if not user:
        user = state.request.user
    if user.is_authenticated and user.timezone:
        tz = user.timezone
        value = value.astimezone(tz)
    return date(value, arg)


@register.filter(expects_localtime=True, is_safe=False)
def usertime(value: datetime | None, user: "User|AnonymousUser|None" = None, arg: str = "H:i") -> str:
    if not value:
        return ""
    if not user:
        user = state.request.user
    if user.is_authenticated and user.timezone:
        tz = user.timezone
        value = value.astimezone(tz)
    return date(value, arg)
