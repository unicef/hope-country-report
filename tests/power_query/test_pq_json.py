import uuid

import pytest
from django.utils import timezone

from hope_country_report.apps.core.models import User
from hope_country_report.apps.power_query.json import PQJSONEncoder


@pytest.mark.parametrize("value", [uuid.uuid4(), User(username="username", id=1), timezone.now()])
def test_encode(value):
    enc = PQJSONEncoder()
    assert enc.default(value), value
