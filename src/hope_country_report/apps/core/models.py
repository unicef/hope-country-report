import datetime
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.gis.db.models import MultiPolygonField
from django.db import models
from django.db.models import QuerySet
from django.urls import reverse
from django.utils import dateformat
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from timezone_field import TimeZoneField
from unicef_security.models import AbstractUser

from hope_country_report.apps.hope.models import BusinessArea
from hope_country_report.state import state


class CountryOfficeManager(models.Manager["CountryOffice"]):
    def get_queryset(self) -> QuerySet["CountryOffice"]:
        if state.tenant:
            return super().get_queryset().filter(id=state.tenant.pk)
        return super().get_queryset()


class CountryOffice(models.Model):
    HQ = "HQ"
    name = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=False, blank=True)
    code = models.CharField(max_length=10, unique=True, blank=True)
    long_name = models.CharField(max_length=255, blank=True)
    region_code = models.CharField(max_length=8, blank=True)
    region_name = models.CharField(max_length=8, blank=True)
    hope_id = models.CharField(unique=True, max_length=100, blank=True)
    slug = models.SlugField(unique=True)

    timezone = TimeZoneField(verbose_name=_("Timezone"), default="UTC", help_text=_("Country default timezone."))
    locale = models.CharField(
        verbose_name=_("Locale"),
        max_length=10,
        choices=settings.LANGUAGES,
        default="en",
        help_text=_("Country default locale. It affects dates and number formats"),
    )
    settings = models.JSONField(default=dict, blank=True)

    objects = CountryOfficeManager()

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    @cached_property
    def business_area(self) -> "BusinessArea|None":
        from hope_country_report.apps.hope.models import BusinessArea

        return BusinessArea.objects.filter(id=self.hope_id).first()

    @cached_property
    def shape(self) -> "CountryShape|None":
        return CountryShape.objects.get(pk=self.settings.get("map"))

    def get_map_settings(self) -> dict[str, int | float]:
        lat = self.settings.get("map", {}).get("center", {}).get("lat", 0)
        lng = self.settings.get("map", {}).get("center", {}).get("lng", 0)
        zoom = self.settings.get("map", {}).get("zoom", 8)
        return {
            "lat": lat,
            "lng": lng,
            "zoom": zoom,
        }

    @classmethod
    def sync(cls) -> None:
        from hope_country_report.apps.hope.models import BusinessArea

        CountryOffice.objects.update_or_create(
            hope_id=CountryOffice.HQ,
            defaults={
                "name": "Headquarter",
                "slug": "-",
                "long_name": "Headquarter",
                "active": True,
                "code": CountryOffice.HQ,
            },
        )

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

    def get_absolute_url(self) -> str:
        return reverse("office-index", args=[self.slug])


DATE_FORMATS: list[tuple[str, str]]
TIME_FORMATS: list[tuple[str, str]]
sample = datetime.datetime(2000, 12, 31, 23, 59)

DATE_FORMATS = [(fmt, dateformat.format(sample, fmt)) for fmt in ["Y M d", "j M Y", "Y-m-d", "Y M d, l", "D, j M Y"]]
TIME_FORMATS = [(fmt, dateformat.format(sample, fmt)) for fmt in ["h:i a", "H:i"]]


class User(AbstractUser):  # type: ignore
    timezone: ZoneInfo
    timezone = TimeZoneField(verbose_name=_("Timezone"), default="UTC")
    language = models.CharField(verbose_name=_("Language"), max_length=10, choices=settings.LANGUAGES, default="en")
    date_format = models.CharField(
        verbose_name=_("Date Format"),
        max_length=20,
        choices=DATE_FORMATS,
        default=DATE_FORMATS[0][0],
        help_text=_("Only applied to user interface. It will not be applied to the reports"),
    )
    time_format = models.CharField(
        verbose_name=_("Date Format"),
        max_length=20,
        choices=TIME_FORMATS,
        default=TIME_FORMATS[0][0],
        help_text=_("Only applied to user interface. It will not be applied to the reports"),
    )

    @cached_property
    def datetime_format(self) -> str:
        return f"{self.date_format} {self.time_format}"

    class Meta:
        app_label = "core"
        swappable = "AUTH_USER_MODEL"

    @cached_property
    def friendly_name(self) -> str:
        return self.first_name or self.username

    @cached_property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}" or self.username


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roles")
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE)
    expires = models.DateField(blank=True, null=True)

    class Meta:
        app_label = "core"
        unique_together = ("user", "group", "country_office")

    def __str__(self) -> str:
        return f"{self.user.username} {self.group.name}"


class CountryShape(models.Model):
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    fips = models.CharField("FIPS Code", max_length=2, null=True)
    iso2 = models.CharField("2 Digit ISO", max_length=2)
    iso3 = models.CharField("3 Digit ISO", max_length=3)
    un = models.IntegerField("United Nations Code")
    region = models.IntegerField("Region Code")
    subregion = models.IntegerField("Sub-Region Code")
    lon = models.FloatField()
    lat = models.FloatField()

    mpoly = MultiPolygonField(null=True)
