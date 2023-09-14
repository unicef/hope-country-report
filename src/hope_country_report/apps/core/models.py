from django.contrib.auth.models import Group
from django.db import models

from unicef_security.models import AbstractUser


class User(AbstractUser):  # type: ignore
    class Meta:
        app_label = "core"


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userrole")
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    business_area = models.UUIDField()

    class Meta:
        app_label = "core"
