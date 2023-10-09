from django.contrib.auth.models import Group
from django.db import models
from django.utils.functional import cached_property
from django.utils.text import slugify

from unicef_security.models import AbstractUser

from hope_country_report.apps.hope.models import BusinessArea


class CountryOfficeManager(models.Manager["CountryOffice"]):
    ...
    # def get_queryset(self):
    #     if is_tenant_active():
    #         if active_tenant := get_selected_tenant():
    #             ...
    #     #         return super().get_queryset().filter(id=active_tenant.pk)
    #     return super().get_queryset()


class CountryOffice(models.Model):
    name = models.CharField(max_length=100, editable=False, blank=True)
    active = models.BooleanField(default=False, blank=True)
    code = models.CharField(max_length=10, unique=True, blank=True)
    long_name = models.CharField(max_length=255, blank=True)
    region_code = models.CharField(max_length=8, blank=True)
    region_name = models.CharField(max_length=8, blank=True)
    hope_id = models.CharField(unique=True, max_length=100, blank=True)
    slug = models.SlugField()

    objects = CountryOfficeManager()

    class Meta:
        ordering = ("name",)

    @cached_property
    def business_area(self) -> "BusinessArea|None":
        return BusinessArea.objects.filter(id=self.hope_id).first()

    @classmethod
    def sync(cls) -> None:
        from hope_country_report.apps.hope.models import BusinessArea

        for ba in BusinessArea.objects.all():
            values = {
                "hope_id": str(ba.id),
                "name": ba.name,
                "active": ba.active,
                "code": ba.code,
                "long_name": ba.long_name,
                "region_code": ba.region_code,
                "slug": slugify(ba.name),
            }
            CountryOffice.objects.update_or_create(hope_id=ba.id, defaults=values)

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):  # type: ignore
    class Meta:
        app_label = "core"


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roles")
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE)
    expires = models.DateField(blank=True, null=True)

    class Meta:
        app_label = "core"
        unique_together = ("user", "group", "country_office")

    def __str__(self) -> str:
        return "%s %s" % (self.user.username, self.group.name)
