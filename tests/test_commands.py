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
def test_upgrade(options, monkeypatch):
    out = StringIO()
    call_command("upgrade", stdout=out, check=False, **options)
    assert "Running upgrade" in str(out.getvalue())
    assert "Upgrade completed" in str(out.getvalue())


def test_upgrade_check(mocked_responses):
    out = StringIO()
    environ = {k: v for k, v in os.environ.items() if k not in ["FERNET_KEYS"]}
    with mock.patch.dict(os.environ, environ, clear=True):
        call_command("upgrade", stdout=out, check=True)


@pytest.mark.parametrize("template", [True, False], ids=["template", ""])
@pytest.mark.parametrize("comment", [True, False], ids=["comment", ""])
@pytest.mark.parametrize("group", ("mandatory", "optional", "all", "develop"))
@pytest.mark.parametrize("style", ("dotenv", "direnv", "env"))
def test_env(mocked_responses, template, group, style, comment):
    out = StringIO()
    environ = {"ADMIN_URL_PREFIX": "test"}
    with mock.patch.dict(os.environ, environ, clear=True):
        call_command("env", stdout=out, template=template, group=group, style=style, comment=comment)
        assert "error" not in str(out.getvalue())
