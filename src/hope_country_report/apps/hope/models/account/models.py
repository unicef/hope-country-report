import logging

from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _

from hope_country_report.apps.hope.models._base import HopeModel

logger = logging.getLogger(__name__)

INVITED = "INVITED"
ACTIVE = "ACTIVE"
INACTIVE = "INACTIVE"
USER_STATUS_CHOICES = (
    (ACTIVE, _("Active")),
    (INACTIVE, _("Inactive")),
    (INVITED, _("Invited")),
)


class Partner(HopeModel):
    name = models.CharField(max_length=100, unique=True)
    is_un = models.BooleanField(verbose_name="U.N.", default=False)

    class Meta:
        db_table = "core_datacollectingtype"

    class Tenant:
        tenant_filter_field = "__all__"

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_partners_as_choices(cls) -> list[tuple[id, str]]:
        return [(role.id, role.name) for role in cls.objects.all()]


class User(HopeModel):
    status = models.CharField(choices=USER_STATUS_CHOICES, max_length=10, default=INVITED)
    # org = models.CharField(choices=USER_PARTNER_CHOICES, max_length=10, default=USER_PARTNER_CHOICES.UNICEF)
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, null=True, blank=True)
    email = models.EmailField(_("email address"), blank=True, unique=True)
    available_for_export = models.BooleanField(
        default=True, help_text="Indicating if a User can be exported to CashAssist"
    )
    custom_fields = JSONField(default=dict, blank=True)

    job_title = models.CharField(max_length=255, blank=True)
    ad_uuid = models.CharField(max_length=64, unique=True, null=True, blank=True, editable=False)

    # CashAssist DOAP fields
    last_modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    last_doap_sync = models.DateTimeField(
        default=None, null=True, blank=True, help_text="Timestamp of last sync with CA"
    )

    class Meta:
        db_table = "account_user"

    class Tenant:
        tenant_filter_field = "__all__"


class UserRole(HopeModel):
    business_area = models.ForeignKey("hope.BusinessArea", related_name="user_roles", on_delete=models.CASCADE)
    user = models.ForeignKey("hope.User", related_name="user_roles", on_delete=models.CASCADE)
    role = models.ForeignKey("hope.Role", related_name="user_roles", on_delete=models.CASCADE)

    class Meta:
        db_table = "account_userrole"

    class Tenant:
        tenant_filter_field = "business_area"

    def __str__(self) -> str:
        return f"{self.user} {self.role} in {self.business_area}"


#
# class UserGroup(HopeModel):
#     business_area = models.ForeignKey("hope.BusinessArea", related_name="user_groups", on_delete=models.CASCADE)
#     user = models.ForeignKey("hope.User", related_name="user_groups", on_delete=models.CASCADE)
#     group = models.ForeignKey(Group, related_name="user_groups", on_delete=models.CASCADE)
#
#
#     class Meta:
#         db_table = "account_user_group"
#
#     class Tenant:
#         tenant_filter_field = "business_area"
#
#     def __str__(self) -> str:
#         return f"{self.user} {self.group} in {self.business_area}"


class Role(HopeModel):
    API = "API"
    HOPE = "HOPE"
    KOBO = "KOBO"
    CA = "CA"
    SUBSYSTEMS = (
        (HOPE, "HOPE"),
        (KOBO, "Kobo"),
        (CA, "CashAssist"),
        (API, "API"),
    )

    name = models.CharField(max_length=250)
    subsystem = models.CharField(choices=SUBSYSTEMS, max_length=30, default=HOPE)

    class Meta:
        db_table = "account_role"

    class Tenant:
        tenant_filter_field = "__all__"
