from typing import Any

import logging
import random
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    requires_migrations_checks = False
    requires_system_checks = []

    def handle(self, *args: Any, **options: Any) -> None:
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.sites.models import Site

        from flags.models import FlagState

        from hope_country_report.apps.core.models import CountryOffice, User
        from hope_country_report.apps.hope.models import Household
        from hope_country_report.apps.power_query.models import Formatter, Parametrizer, Query, ReportConfiguration

        Site.objects.update_or_create(
            pk=settings.SITE_ID,
            defaults={
                "domain": "localhost:8000",
                "name": "localhost",
            },
        )
        Site.objects.clear_cache()

        for flag in settings.FLAGS.keys():
            FlagState.objects.get_or_create(name=flag, condition="hostname", value="127.0.0.1,localhost")

        reporters = Group.objects.get(name=settings.REPORTERS_GROUP_NAME)
        afg, __ = CountryOffice.objects.get_or_create(slug="afghanistan")
        user, __ = User.objects.get_or_create(username="user")
        user.roles.get_or_create(group=reporters, country_office=afg)
        p, __ = Parametrizer.objects.get_or_create(
            name="months", value={"month": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}
        )
        q1 = Query.objects.get_or_create(
            name="Full HH list",
            defaults=dict(country_office=afg, owner=user, target=ContentType.objects.get_for_model(Household)),
        )[0]
        q2 = Query.objects.get_or_create(
            name="Monthly registrations: {monthname}",
            defaults=dict(
                country_office=afg,
                parametrizer=p,
                code="""import calendar
month=args['month']
result=conn.filter(first_registration_date__month=month)
extra={"monthname": calendar.month_name[month]}
""",
                owner=user,
                target=ContentType.objects.get_for_model(Household),
            ),
        )[0]
        q3 = Query.objects.get_or_create(
            name="Programme List",
            defaults=dict(
                country_office=afg,
                owner=user,
                target=ContentType.objects.get_for_model(Household),
                code="""result=conn.all()""",
            ),
        )[0]

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

        tags = ["tag%d" % d for d in range(10)]
        for q in [q1, q2, q3]:
            r = ReportConfiguration.objects.get_or_create(
                title=q.name,
                country_office=q.country_office,
                defaults={"query": q, "owner": q.owner, "context": {"extra_footer": "-- Report footer --"}},
            )[0]
            r.formatters.add(*Formatter.objects.all())
            r.tags.add(*random.choices(tags, k=random.choice([1, 2, 3])))

        CountryOffice.objects.filter(
            slug__in=[
                "south-sudan",
                "sudan",
                "ukraine",
                "afghanistan",
                "democratic-republic-of-congo",
                "sri-lanka",
                "barbados",
                "bangladesh",
                "central-african-republic",
                "niger",
                "palestine-state-of",
                "philippines",
                "slovakia",
                "trinidad-tobago",
            ]
        ).update(active=True)

        for params in [
            {"compress": True, "protect": True},
            {"compress": True},
        ]:
            r = ReportConfiguration.objects.get_or_create(
                name=f"{urlencode(params)}",
                title=f"{urlencode(params)}",
                country_office=q2.country_office,
                defaults={"query": q2, "owner": q.owner, "context": {"extra_footer": "-- Report footer --"}, **params},
            )[0]
            r.formatters.add(*Formatter.objects.all())
            r.tags.add(*random.choices(tags, k=random.choice([1, 2, 3])))
            print("--------", r.pk, r.name)

        for r in ReportConfiguration.objects.all():
            r.execute(True, notify=False)
