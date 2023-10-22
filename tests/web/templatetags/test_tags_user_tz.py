import zoneinfo

from django.utils.timezone import now

import freezegun

from hope_country_report.web.templatetags.user_tz import userdatetime


@freezegun.freeze_time("2000-01-01 08:00:00 UTC")
def test_userdatetime(user):
    user.timezone = zoneinfo.ZoneInfo("UTC")
    assert userdatetime(now(), user) == "2000 Jan 01 08:00"
    user.timezone = zoneinfo.ZoneInfo("Europe/Rome")
    assert userdatetime(now(), user) == "2000 Jan 01 09:00"
