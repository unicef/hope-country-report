import logging
from typing import Any

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
        from hope_country_report.apps.power_query.models import Query

        FlagState.objects.get_or_create(name="DEVELOP_DEBUG_TOOLBAR", condition="hostname", value="127.0.0.1,localhost")
        FlagState.objects.get_or_create(name="DEVELOP_DEBUG_TOOLBAR", condition="superuser", value="1", required=True)
        reporters = Group.objects.get(name=settings.REPORTERS_GROUP_NAME)
        afg, __ = CountryOffice.objects.get_or_create(slug="afghanistan")
        user, __ = User.objects.get_or_create(username="user")
        user.roles.get_or_create(group=reporters, country_office=afg)

        Query.objects.get_or_create(
            name="Full HH list",
            defaults=dict(project=afg, owner=user, target=ContentType.objects.get_for_model(Household)),
        )
