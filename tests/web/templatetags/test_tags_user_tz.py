import zoneinfo

import freezegun
from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import now
from testutils.perms import set_current_user

from hope_country_report.web.templatetags.user_tz import userdatetime


@freezegun.freeze_time("2000-01-01 08:00:00 UTC")
def test_userdatetime_nouser():
    timestamp = now()
    assert userdatetime(timestamp) == "2000 Jan 01 08:00 a.m."
    assert userdatetime(timestamp, "dt") == "2000 Jan 01 08:00 a.m."
    assert userdatetime(timestamp, "d") == "2000 Jan 01"
    assert userdatetime(timestamp, "t") == "08:00 a.m."
    assert userdatetime(timestamp, "-") == "08:00 a.m."

    with freezegun.freeze_time("2000-12-01 08:00:00 UTC"):
        assert userdatetime(timestamp, "-") == "2000 Jan 01"


@freezegun.freeze_time("2000-01-01 08:00:00 UTC")
def test_userdatetime_authenticated(user):
    user.timezone = zoneinfo.ZoneInfo("UTC")
    timestamp = now()
    with set_current_user(user):
        assert userdatetime(timestamp) == "2000 Jan 01 08:00 a.m."

        user.timezone = zoneinfo.ZoneInfo("Europe/Rome")
        assert userdatetime(timestamp) == "2000 Jan 01 09:00 a.m."

        assert userdatetime(timestamp, "dt") == "2000 Jan 01 09:00 a.m."
        assert userdatetime(timestamp, "d") == "2000 Jan 01"
        assert userdatetime(timestamp, "t") == "09:00 a.m."

        with freezegun.freeze_time("2000-12-01 08:00:00 UTC"):
            assert userdatetime(timestamp, "-") == "2000 Jan 01"


@freezegun.freeze_time("2000-01-01 08:00:00 UTC")
def test_userdatetime_anon():
    with set_current_user(AnonymousUser()):
        assert userdatetime(now()) == "2000 Jan 01 08:00 a.m."

        assert userdatetime(now(), "dt") == "2000 Jan 01 08:00 a.m."
        assert userdatetime(now(), "d") == "2000 Jan 01"
        assert userdatetime(now(), "t") == "08:00 a.m."

        assert userdatetime(now(), "-") == "08:00 a.m."


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
