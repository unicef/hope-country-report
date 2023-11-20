from django.db.models import ManyToManyField

from hope_country_report.apps.hope.models import BusinessArea
from hope_country_report.apps.hope.patcher.ba import BusinessAreaManager

class _BusinessArea(BusinessArea):
    objects: BusinessAreaManager
    countries: ManyToManyField
