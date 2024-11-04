import os
from io import StringIO

import pytest
from unittest import mock

from django.core.management import call_command

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "options",
    [
        {},
        {"admin_email": "user@test.com", "admin_password": 123},
    ],
)
@pytest.mark.parametrize("verbosity", [1, 0], ids=["verbose", ""])
@pytest.mark.parametrize("migrate", [1, 0], ids=["migrate", ""])
def test_upgrade(options, verbosity, migrate, monkeypatch):
    out = StringIO()
    call_command("upgrade", stdout=out, check=False, verbosity=verbosity, **options)
    assert "error" not in str(out.getvalue())


def test_upgrade_check(mocked_responses):
    out = StringIO()
    environ = {k: v for k, v in os.environ.items() if k not in ["FERNET_KEYS"]}
    with mock.patch.dict(os.environ, environ, clear=True):
        call_command("upgrade", stdout=out, check=True)
