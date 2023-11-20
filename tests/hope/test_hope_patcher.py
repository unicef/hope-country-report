from hope_country_report.apps.core.models import CountryOffice
from testutils.factories import CountryFactory


def test_ba_m2m(afghanistan: "CountryOffice"):
    afg = CountryFactory()
    afghanistan.business_area.countries.add(afg)
    assert afghanistan.business_area.countries.filter(id=afg.pk).exists()
