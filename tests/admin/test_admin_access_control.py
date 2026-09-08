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
        ChartPageFactory(
            country_office=afghanistan, query=QueryFactory(country_office=afghanistan), title="AFG chart"
        )
        ChartPageFactory(country_office=niger, query=QueryFactory(country_office=niger), title="NER chart")
    return {"co": afghanistan, "niger": niger}


def test_admin_requires_staff(django_app, user):
    """A non-staff authenticated user must not get access to the admin panel."""
    res = django_app.get("/admin/", user=user)
    assert res.status_code == 302
    assert "/admin/login/" in res.location


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
