from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models

if TYPE_CHECKING:
    from hope_country_report.types.django import AnyModel


def get_or_create_reporter_group() -> "Group":
    """Create the (empty) Reporters group if missing.

    Permissions are assigned by administrators through the Django admin, not by
    application code.
    """
    group, _ = Group.objects.get_or_create(name=settings.REPORTERS_GROUP_NAME)
    return group


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
