from hope_country_report.apps.power_query.exceptions import QueryRunError


def test_queryrunerror():
    assert str(QueryRunError(ValueError("abc"))) == "ValueError: abc"
