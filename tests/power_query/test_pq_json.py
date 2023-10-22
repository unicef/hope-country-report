import uuid

import pytest

from hope_country_report.apps.core.models import User
from hope_country_report.apps.power_query.json import PQJSONEncoder


@pytest.mark.parametrize("value", [uuid.uuid4(), User()])
def test_encode(value):
    enc = PQJSONEncoder()
    assert enc.encode(value)
