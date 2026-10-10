from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.db import models

if TYPE_CHECKING:
    from hope_country_report.types.django import AnyModel


# Minimal privileges for report consumers. Authoring Query.code/templates is a
# code-execution surface and is deliberately excluded (see QUERY_AUTHOR_PERMISSIONS).
REPORTER_PERMISSIONS = (
    "view_reportconfiguration",
    "change_reportconfiguration",
    "view_reportdocument",
    "download_reportdocument",
    "view_chartpage",
)

# Privileges for the QueryUsers authoring group.
QUERY_AUTHOR_PERMISSIONS = (
    "add_query",
    "change_query",
    "delete_query",
    "view_query",
    "add_parametrizer",
    "change_parametrizer",
    "delete_parametrizer",
    "view_parametrizer",
    "add_formatter",
    "change_formatter",
    "delete_formatter",
    "view_formatter",
    "add_reporttemplate",
    "change_reporttemplate",
    "delete_reporttemplate",
    "view_reporttemplate",
    "add_chartpage",
    "change_chartpage",
    "delete_chartpage",
    "view_chartpage",
    "add_reportconfiguration",
    "change_reportconfiguration",
    "delete_reportconfiguration",
    "view_reportconfiguration",
    "view_dataset",
    "view_reportdocument",
    "download_reportdocument",
)


def _power_query_permissions(codenames: "tuple[str, ...]") -> "models.QuerySet[Permission]":
    return Permission.objects.filter(content_type__app_label="power_query", codename__in=codenames)


def get_or_create_reporter_group() -> "Group":
    reporter, _ = Group.objects.get_or_create(name=settings.REPORTERS_GROUP_NAME)
    # set() (not add()) so pre-existing broad grants are reconciled on upgrade.
    reporter.permissions.set(_power_query_permissions(REPORTER_PERMISSIONS))
    return reporter


def get_or_create_query_user_group() -> "Group":
    group, _ = Group.objects.get_or_create(name=settings.QUERY_AUTHOR_GROUP_NAME)
    group.permissions.set(_power_query_permissions(QUERY_AUTHOR_PERMISSIONS))
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
