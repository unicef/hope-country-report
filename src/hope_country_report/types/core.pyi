from typing import Any

from django.contrib.gis.db.models import MultiPolygonField

from hope_country_report.apps.core.models import CountryOffice, CountryShape, User, UserRole
from hope_country_report.types.hope import TBusinessArea

class TCountryOffice(CountryOffice):
    objects: Any
    geom: MultiPolygonField[Any, Any] | None
    business_area: TBusinessArea | None

class TUser(User): ...
class TUserRole(UserRole): ...
class TCountryShape(CountryShape): ...
