import zoneinfo

from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import now

import freezegun
from testutils.perms import set_current_user

from hope_country_report.web.templatetags.user_tz import userdatetime


@freezegun.freeze_time("2000-01-01 08:00:00 UTC")
def test_userdate(user):
    user.timezone = zoneinfo.ZoneInfo("UTC")
    with set_current_user(user):
        assert userdatetime(now()) == "2000 Jan 01 08:00 a.m."

        user.timezone = zoneinfo.ZoneInfo("Europe/Rome")
        assert userdatetime(now()) == "2000 Jan 01 09:00 a.m."

    with set_current_user(AnonymousUser()):
        assert userdatetime(now()) == "2000 Jan 01 08:00 a.m."

    assert userdatetime(None) == ""

    assert userdatetime(now()) == "2000 Jan 01 08:00 a.m."


@freezegun.freeze_time("2000-01-01 08:00:00 UTC")
def test_usertime(user):
    user.timezone = zoneinfo.ZoneInfo("UTC")
    with set_current_user(user):
        assert userdatetime(now(), "h:i a") == "08:00 a.m."

        user.timezone = zoneinfo.ZoneInfo("Europe/Rome")
        assert userdatetime(now(), "h:i a") == "09:00 a.m."

    with set_current_user(AnonymousUser()):
        assert userdatetime(now(), "h:i a") == "08:00 a.m."

    assert userdatetime(None) == ""

    assert userdatetime(now(), "h:i a") == "08:00 a.m."
