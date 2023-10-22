from typing import Any

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import MultipleObjectsReturned
from django.db import models

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
    def get(self, *args: Any, **kwargs: Any) -> AnyModel:
        try:
            return super().get(*args, **kwargs)
        except MultipleObjectsReturned as e:
            raise MultipleObjectsReturned(f"{e} {args} {kwargs}")
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist(
                "%s matching query does not exist. Using %s %s" % (self.model._meta.object_name, args, kwargs)
            )


class SmartManager(models.Manager[AnyModel]):
    _queryset_class = SmartQuerySet
