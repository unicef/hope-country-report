def test_dbrouters():
    from hope_country_report.apps.core.dbrouters import DbRouter
    from hope_country_report.apps.hope.models import Household

    r = DbRouter()
    assert r.select_db(Household) == "hope_ro"
    assert r.db_for_read(Household) == "hope_ro"
    assert r.db_for_write(Household) == "hope_ro"
    assert not r.allow_migrate("hope_ro", "hope")
    assert r.allow_migrate("default", "core")
    assert r.allow_migrate("default", "power_query")
