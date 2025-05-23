from typing import TYPE_CHECKING

from testutils.factories import CountryFactory

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice


def test_ba_m2m(afghanistan: "CountryOffice"):
    afg = CountryFactory()
    afghanistan.business_area.countries.add(afg)
    assert afghanistan.business_area.countries.filter(id=afg.pk).exists()
