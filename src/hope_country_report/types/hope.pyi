from django.db.models import ManyToManyField, QuerySet

from hope_country_report.apps.hope.models import BusinessArea, Country
from hope_country_report.apps.hope.patcher.ba import BusinessAreaManager

class TBusinessArea(BusinessArea):
    objects: BusinessAreaManager
    countries: QuerySet[Country]
