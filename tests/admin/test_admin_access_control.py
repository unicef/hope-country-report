from unittest import mock

import pytest
from django.urls import reverse

from hope_country_report.state import state

pytestmark = [pytest.mark.django_db]


@pytest.fixture()
def staff_role_user(afghanistan):
    """A staff (non-superuser) user restricted to the Afghanistan office."""
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType

    from hope_country_report.apps.power_query.models import ChartPage

    from testutils.factories import UserFactory, UserRoleFactory

    u = UserFactory(username="staff_role", is_staff=True, is_superuser=False, is_active=True)
    ct = ContentType.objects.get_for_model(ChartPage)
    perm = Permission.objects.get(content_type=ct, codename="view_chartpage")
    u.user_permissions.add(perm)
    role_group, _ = Group.objects.get_or_create(name="Chart Viewers")
    UserRoleFactory(user=u, group=role_group, country_office=afghanistan)
    return u


@pytest.fixture()
def chart_data(afghanistan):
    from testutils.factories import ChartPageFactory, CountryOfficeFactory, QueryFactory

    niger = CountryOfficeFactory(name="Niger")
    with state.set(must_tenant=False):
        ChartPageFactory(country_office=afghanistan, query=QueryFactory(country_office=afghanistan), title="AFG chart")
        ChartPageFactory(country_office=niger, query=QueryFactory(country_office=niger), title="NER chart")
    return {"co": afghanistan, "niger": niger}


ADMIN_GET_URLS = [
    "admin:index",
    "admin:core_user_changelist",
    "admin:power_query_query_changelist",
    "admin:power_query_dataset_changelist",
    "admin:power_query_reportconfiguration_changelist",
    "admin:power_query_reportdocument_changelist",
    "admin:power_query_formatter_changelist",
    "admin:power_query_reporttemplate_changelist",
    "admin:power_query_chartpage_changelist",
    "admin:power_query_parametrizer_changelist",
]


def test_admin_requires_staff(django_app, user):
    """A non-staff authenticated user must not get access to the admin panel."""
    res = django_app.get("/admin/", user=user)
    assert res.status_code == 302
    assert "/admin/login/" in res.location


@pytest.mark.parametrize("url_name", ADMIN_GET_URLS)
def test_all_admin_changelists_require_staff(django_app, user, url_name):
    """Every admin changelist must redirect a non-staff user to the login page."""
    res = django_app.get(reverse(url_name), user=user)
    assert res.status_code == 302
    assert "/admin/login/" in res.location


@pytest.mark.parametrize(
    ("url_name", "args"),
    [
        ("admin:power_query_query_add", []),
        ("admin:power_query_query_change", [1]),
        ("admin:power_query_query_explain", [1]),
        ("admin:core_user_change", [1]),
    ],
)
def test_admin_object_views_require_staff(django_app, user, url_name, args):
    """Non-staff users must be blocked before any object lookup on admin views."""
    res = django_app.get(reverse(url_name, args=args), user=user)
    assert res.status_code == 302
    assert "/admin/login/" in res.location


def test_staff_can_reach_power_query_admin(django_app, admin_user):
    res = django_app.get(reverse("admin:power_query_query_changelist"), user=admin_user)
    assert res.status_code == 200


def test_hope_models_are_not_registered_in_admin(db, admin_user):
    from django.contrib.admin.sites import site

    assert not [m for m in site._registry if m._meta.app_label == "hope"]


def test_hope_admin_url_unreachable(django_app, admin_user):
    res = django_app.get("/admin/hope/household/", user=admin_user, expect_errors=True)
    assert res.status_code == 404


def _query_admin():
    from django.contrib.admin.sites import site

    from hope_country_report.apps.power_query.models import Query

    return site._registry[Query]


def test_non_author_cannot_edit_query(afghanistan, reporters):
    """Holding change_query is not enough: authoring requires the QueryUsers group."""
    from unittest.mock import Mock

    from django.contrib.auth.models import Permission

    from testutils.factories import UserFactory, UserRoleFactory

    user = UserFactory(username="non_author", is_staff=True, is_active=True)
    UserRoleFactory(user=user, group=reporters, country_office=afghanistan)
    user.user_permissions.add(Permission.objects.get(content_type__app_label="power_query", codename="change_query"))
    request = Mock(user=user)
    admin = _query_admin()
    assert admin.has_change_permission(request) is False
    assert admin.has_add_permission(request) is False


def test_query_author_can_edit_query(db):
    from unittest.mock import Mock

    from hope_country_report.apps.core.utils import get_or_create_query_user_group

    from testutils.factories import UserFactory

    group = get_or_create_query_user_group()
    user = UserFactory(username="author", is_staff=True, is_active=True)
    user.groups.add(group)
    request = Mock(user=user)
    admin = _query_admin()
    assert admin.has_change_permission(request) is True
    assert admin.has_add_permission(request) is True


def test_generated_artifacts_are_read_only(db):
    from unittest.mock import Mock

    from django.contrib.admin.sites import site

    from hope_country_report.apps.power_query.models import Dataset, ReportDocument

    user = Mock(is_superuser=False, is_active=True, is_staff=True)
    superuser = Mock(is_superuser=True, is_active=True, is_staff=True)
    for model in (Dataset, ReportDocument):
        model_admin = site._registry[model]
        assert model_admin.has_add_permission(Mock(user=user)) is False
        assert model_admin.has_change_permission(Mock(user=user)) is False
        assert model_admin.has_delete_permission(Mock(user=user)) is False
        # superusers may delete for maintenance, but never edit the stored file
        assert model_admin.has_change_permission(Mock(user=superuser)) is False
        assert model_admin.has_delete_permission(Mock(user=superuser)) is True


def test_expired_role_staff_sees_no_objects(django_app, afghanistan, reporters):
    """A staff user whose only UserRole has expired must see no tenant objects."""
    from datetime import date

    from django.contrib.auth.models import Permission

    from testutils.factories import QueryFactory, UserFactory, UserRoleFactory

    user = UserFactory(username="expired_staff", is_staff=True, is_active=True)
    UserRoleFactory(user=user, group=reporters, country_office=afghanistan, expires=date(2020, 1, 1))
    user.user_permissions.add(Permission.objects.get(content_type__app_label="power_query", codename="view_query"))
    with state.set(must_tenant=False):
        QueryFactory(country_office=afghanistan, name="expired-role-query")

    res = django_app.get(reverse("admin:power_query_query_changelist"), user=user)
    assert res.status_code == 200
    assert "expired-role-query" not in res.text


def test_admin_index_superuser(django_app, admin_user):
    res = django_app.get("/admin/", user=admin_user)
    assert res.status_code == 200


def test_admin_chartpage_list_scoped_to_selected_tenant(django_app, staff_role_user, chart_data):
    """Staff users only see ChartPages of their selected CountryOffice."""
    with mock.patch("hope_country_report.apps.tenant.utils.get_selected_tenant", return_value=chart_data["co"]):
        res = django_app.get(reverse("admin:power_query_chartpage_changelist"), user=staff_role_user)
    assert res.status_code == 200
    assert "AFG chart" in res.text
    assert "NER chart" not in res.text


def test_admin_chartpage_list_empty_without_selected_tenant(django_app, staff_role_user, chart_data):
    """Without a selected tenant a staff user must not see other offices' objects."""
    with mock.patch("hope_country_report.apps.tenant.utils.get_selected_tenant", return_value=None):
        res = django_app.get(reverse("admin:power_query_chartpage_changelist"), user=staff_role_user)
    assert res.status_code == 200
    assert "AFG chart" not in res.text
    assert "NER chart" not in res.text
