from typing import Any

import logging

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    requires_migrations_checks = False
    requires_system_checks = []

    def handle(self, *args: Any, **options: Any) -> None:
        from django.contrib.contenttypes.models import ContentType

        from flags.models import FlagState

        from hope_country_report.apps.core.models import CountryOffice, User
        from hope_country_report.apps.hope.models import Household
        from hope_country_report.apps.power_query.models import Formatter, Query, Report

        FlagState.objects.get_or_create(name="DEVELOP_DEBUG_TOOLBAR", condition="hostname", value="127.0.0.1,localhost")
        FlagState.objects.get_or_create(name="DEVELOP_DEBUG_TOOLBAR", condition="debug", value="1", required=True)
        reporters = Group.objects.get(name=settings.REPORTERS_GROUP_NAME)
        afg, __ = CountryOffice.objects.get_or_create(slug="afghanistan")
        user, __ = User.objects.get_or_create(username="user")
        user.roles.get_or_create(group=reporters, country_office=afg)

        q, __ = Query.objects.get_or_create(
            name="Full HH list",
            defaults=dict(country_office=afg, owner=user, target=ContentType.objects.get_for_model(Household)),
        )

        r1, __ = Report.objects.get_or_create(
            title="Full HH list", country_office=afg, defaults={"query": q, "owner": user}
        )
        r1.formatters.add(*Formatter.objects.all())
        r1.tags.add("tag1", "tag2")

        r2, __ = Report.objects.get_or_create(
            title="Report #2", country_office=afg, defaults={"query": q, "owner": user}
        )
        r2.tags.add("tag1", "tag3", "tag4")

        Query.objects.get_or_create(
            name="Dev Query",
            defaults=dict(
                country_office=afg,
                owner=None,
                target=ContentType.objects.get_for_model(Household),
                code="""import time
start=time.time()
while True:
    time.sleep(1)
    print(f"Query: {self} -  Aborted: {self.is_aborted()}")
""",
            ),
        )
