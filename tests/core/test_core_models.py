from unittest.mock import patch

import pytest

from hope_country_report.apps.core.models import CountryOffice, CountryShape, User, UserRole


def test_country_shape_create(db):
    cs = CountryShape.objects.create(name="Test", iso2="TS", iso3="TST")
    assert cs.name == "Test"
    assert str(cs) == "Test"


def test_country_shape_str(db):
    cs = CountryShape.objects.create(name="Afghanistan", iso2="AF")
    assert str(cs) == "Afghanistan"


def test_country_office_create(db):
    co = CountryOffice.objects.create(
        name="Test Office",
        slug="test-office",
        code="TO",
        active=True,
    )
    assert co.pk is not None
    assert co.name == "Test Office"


def test_country_office_str(co):
    assert str(co) == "Test Office"


def test_hq_constant():
    assert CountryOffice.HQ == "HQ"


def test_country_office_get_map_settings_defaults(co):
    settings = co.get_map_settings()
    assert settings == {"lat": 0, "lng": 0, "zoom": 8}


def test_country_office_get_map_settings_custom(co):
    co.settings = {"map": {"center": {"lat": 34.5, "lng": 69.2}, "zoom": 10}}
    co.save()
    settings = co.get_map_settings()
    assert settings == {"lat": 34.5, "lng": 69.2, "zoom": 10}


def test_country_office_business_area_is_none_for_hq(co):
    co.hope_id = CountryOffice.HQ
    co.save()
    assert co.business_area is None


def test_country_office_business_area_is_none_for_null_hope_id(co):
    co.hope_id = None
    co.save()
    assert co.business_area is None


def test_country_office_get_absolute_url(co):
    url = co.get_absolute_url()
    assert co.slug in url


def test_country_office_default_timezone_is_utc(co):
    assert str(co.timezone) == "UTC"


def test_country_office_default_locale_is_en(co):
    assert co.locale == "en"


def test_user_create(db):
    user = User.objects.create(username="testuser")
    assert user.pk is not None
    assert user.username == "testuser"


def test_user_friendly_name_returns_first_name(db):
    user = User.objects.create(username="jdoe", first_name="John")
    assert user.friendly_name == "John"


def test_user_friendly_name_fallback_to_username(db):
    user = User.objects.create(username="jdoe", first_name="")
    assert user.friendly_name == "jdoe"


def test_user_full_name(db):
    user = User.objects.create(username="jdoe", first_name="John", last_name="Doe")
    assert user.full_name == "John Doe"


def test_user_full_name_when_names_are_empty(db):
    user = User.objects.create(username="jdoe", first_name="", last_name="")
    assert user.full_name == " "


def test_user_datetime_format(db):
    user = User.objects.create(username="jdoe", date_format="Y-m-d", time_format="H:i")
    assert user.datetime_format == "Y-m-d H:i"


def test_user_default_timezone_is_utc(db):
    user = User.objects.create(username="jdoe")
    assert str(user.timezone) == "UTC"


def test_user_default_language_is_en(db):
    user = User.objects.create(username="jdoe")
    assert user.language == "en"


def test_user_date_format_choices(db):
    choices = User._meta.get_field("date_format").choices
    assert len(choices) > 0


def test_user_time_format_choices(db):
    choices = User._meta.get_field("time_format").choices
    assert len(choices) > 0


@pytest.fixture()
def co(db):
    return CountryOffice.objects.create(
        name="Test Office",
        slug="test-office",
        code="TO",
        active=True,
    )


@pytest.fixture()
def role(db, co):
    from django.contrib.auth.models import Group

    user = User.objects.create(username="testuser")
    group = Group.objects.create(name="Test Group")
    return UserRole.objects.create(user=user, group=group, country_office=co)


def test_user_role_create(role):
    assert role.pk is not None


def test_user_role_str(role):
    expected = f"{role.user.username} {role.group.name}"
    assert str(role) == expected


def test_user_role_expires_is_nullable(role):
    assert role.expires is None


def test_user_role_unique_constraint(role):
    with pytest.raises(Exception):
        UserRole.objects.create(
            user=role.user,
            group=role.group,
            country_office=role.country_office,
        )


def test_country_office_manager_sync_creates_hq(db):
    with patch("hope_country_report.apps.hope.models.BusinessArea.objects.all", return_value=[]):
        CountryOffice.objects.sync()
    hq = CountryOffice.objects.get(code=CountryOffice.HQ)
    assert hq.name == "Headquarter"
    assert hq.slug == "-"


def test_country_office_manager_sync_updates_existing(db):
    with patch("hope_country_report.apps.hope.models.BusinessArea.objects.all", return_value=[]):
        CountryOffice.objects.sync()
    hq = CountryOffice.objects.get(code=CountryOffice.HQ)
    original_long_name = hq.long_name
    with patch("hope_country_report.apps.hope.models.BusinessArea.objects.all", return_value=[]):
        CountryOffice.objects.sync()
    hq.refresh_from_db()
    assert hq.long_name == original_long_name
