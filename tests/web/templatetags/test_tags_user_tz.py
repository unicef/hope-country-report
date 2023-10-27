import zoneinfo

from unittest.mock import Mock

from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import now

import freezegun

from hope_country_report.state import state
from hope_country_report.web.templatetags.user_tz import userdatetime, usertime


@freezegun.freeze_time("2000-01-01 08:00:00 UTC")
def test_userdatetime(user):
    user.timezone = zoneinfo.ZoneInfo("UTC")
    assert userdatetime(now(), user) == "2000 Jan 01 08:00"

    user.timezone = zoneinfo.ZoneInfo("Europe/Rome")
    assert userdatetime(now(), user) == "2000 Jan 01 09:00"

    assert userdatetime(now(), AnonymousUser()) == "2000 Jan 01 08:00"

    assert userdatetime(None) == ""

    r = Mock()
    r.user = user
    with state.set(request=r):
        assert userdatetime(now()) == "2000 Jan 01 09:00"


@freezegun.freeze_time("2000-01-01 08:00:00 UTC")
def test_usertime(user):
    user.timezone = zoneinfo.ZoneInfo("UTC")
    assert usertime(now(), user) == "08:00"

    user.timezone = zoneinfo.ZoneInfo("Europe/Rome")
    assert usertime(now(), user) == "09:00"

    assert usertime(now(), AnonymousUser()) == "08:00"

    assert usertime(None) == ""

    r = Mock()
    r.user = user
    with state.set(request=r):
        assert usertime(now()) == "09:00"
