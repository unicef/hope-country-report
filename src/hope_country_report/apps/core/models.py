from django.contrib.auth.models import Group
from django.db import models

from unicef_security.models import AbstractUser


class CountryOffice(models.Model):
    id = models.CharField(primary_key=True, max_length=100, editable=False)
    name = models.CharField(max_length=100, editable=False)
    active = models.BooleanField(default=False)


class User(AbstractUser):  # type: ignore
    class Meta:
        app_label = "core"


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userrole")
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE)

    class Meta:
        app_label = "core"
