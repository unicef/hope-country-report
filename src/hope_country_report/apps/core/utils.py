from typing import Any, TYPE_CHECKING

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.db import models

if TYPE_CHECKING:
    from hope_country_report.types.django import AnyModel


def get_or_create_reporter_group() -> "Group":
    reporter, created = Group.objects.get_or_create(name=settings.REPORTERS_GROUP_NAME)
    # if created:
    for perm in Permission.objects.order_by("codename").filter(
        content_type__app_label="hope", codename__startswith="view_"
    ):
        reporter.permissions.add(perm)
    for perm in Permission.objects.order_by("codename").filter(content_type__app_label="power_query"):
        reporter.permissions.add(perm)

    return reporter


class SmartQuerySet(models.QuerySet["AnyModel"]):
    def get(self, *args: Any, **kwargs: Any) -> "AnyModel":
        try:
            return super().get(*args, **kwargs)
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist(
                f"{self.model._meta.object_name} matching query does not exist. Using {args} {kwargs}"
            )


class SmartManager(models.Manager["AnyModel"]):
    _queryset_class = SmartQuerySet
