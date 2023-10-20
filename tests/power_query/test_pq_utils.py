from base64 import b64encode
from pathlib import Path

import pytest

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse

import tablib

from hope_country_report.apps.power_query.utils import basicauth, is_valid_template, sizeof, to_dataset


@pytest.mark.parametrize(
    "value, expected",
    [
        ("a.docx", True),
        ("a.pdf", True),
        ("a.mov", False),
        ("~.pdf", False),
        (".a.pdf", False),
    ],
)
def test_is_valid_template(value, expected):
    assert is_valid_template(Path(value)) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (10, "10 b"),
        (1024, "1 Kb"),
        (1500, "1.5 Kb"),
        (1024**10, "1048576.0Yi"),
    ],
)
def test_sizeof(value, expected):
    assert sizeof(value) == expected


def test_to_dataset_qs(user):
    qs = type(user).objects.all()
    assert to_dataset(qs).width == 15


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


def test_basicauth(rf):
    request = rf.get("/")
    request.user = AnonymousUser()
    view = basicauth(lambda request: HttpResponse("Ok"))
    response = view(request)
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


def test_basicauth_authenticate(rf, user):
    request = rf.get(
        "/",
        headers={"Authorization": "Basic " + b64encode(f"{user.username}:password".encode("utf-8")).decode("ascii")},
    )

    request.user = AnonymousUser()
    view = basicauth(lambda request: HttpResponse("Ok"))
    response = view(request)
    assert response.status_code == 200


def test_basicauth_authenticate_fail(rf, user):
    request = rf.get(
        "/",
        headers={"Authorization": "Basic " + b64encode(f"{user.username}:".encode("utf-8")).decode("ascii")},
    )

    request.user = AnonymousUser()
    view = basicauth(lambda request: HttpResponse("Ok"))
    response = view(request)
    assert response.status_code == 200
