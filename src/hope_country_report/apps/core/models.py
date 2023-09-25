from django.contrib.auth.models import Group
from django.db import models

from unicef_security.models import AbstractUser


class CountryOffice(models.Model):
    name = models.CharField(max_length=100, editable=False, blank=True)
    active = models.BooleanField(default=False, blank=True)
    code = models.CharField(max_length=10, unique=True, blank=True)
    long_name = models.CharField(max_length=255, blank=True)
    region_code = models.CharField(max_length=8, blank=True)
    region_name = models.CharField(max_length=8, blank=True)
    hope_id = models.CharField(unique=True, max_length=100, blank=True)

    class Meta:
        ordering = ("name",)

    @classmethod
    def sync(self):
        from hope_country_report.apps.hope.models import BusinessArea

        for el in BusinessArea.objects.all():
            values = {
                "hope_id": str(el.id),
                "name": el.name,
                "active": el.active,
                "code": el.code,
                "long_name": el.long_name,
                "region_code": el.region_code,
            }
            CountryOffice.objects.update_or_create(hope_id=el.id, defaults=values)

    def __str__(self):
        return self.name


class User(AbstractUser):  # type: ignore
    class Meta:
        app_label = "core"


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userrole")
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE)

    class Meta:
        app_label = "core"
