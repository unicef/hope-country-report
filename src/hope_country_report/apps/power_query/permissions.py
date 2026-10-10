from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from hope_country_report.types.django import AnyUser


def is_query_author(user: "AnyUser") -> bool:
    """Return True for superusers and members of the ``QueryUsers`` authoring group.

    Authoring ``Query.code`` (and report templates/formatters) executes code, so
    it is restricted to a dedicated group instead of any staff user.
    """
    if not getattr(user, "is_authenticated", False):
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name=settings.QUERY_AUTHOR_GROUP_NAME).exists()
