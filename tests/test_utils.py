import pytest

import tablib

from hope_country_report.apps.power_query.utils import to_dataset


def test_to_dataset_qs(user):
    qs = type(user).objects.all()
    assert to_dataset(qs).width == 14


def test_to_dataset_values(user):
    qs = type(user).objects.values_list("username")
    assert str(to_dataset(qs)) == "username             \n---------------------\n('user@example.com',)"


def test_to_dataset_iterable(user):
    qs = type(user).objects.values("pk")
    assert to_dataset(list(qs))


def test_to_dataset_dataset():
    data = tablib.Dataset([1, 2])
    assert to_dataset(data)


def test_to_dataset_error():
    with pytest.raises(ValueError):
        assert to_dataset("")
