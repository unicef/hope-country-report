from django.contrib.gis.db.models import PointField
from django.db import models
from django.db.models import JSONField

from .._base import HopeModel
from ..core import BusinessArea


class Household(HopeModel):
    id = models.CharField(primary_key=True, max_length=100, editable=False)
    business_area = models.ForeignKey(BusinessArea, on_delete=models.CASCADE)
    unicef_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    withdrawn = models.BooleanField(default=False, db_index=True)
    withdrawn_date = models.DateTimeField(null=True, blank=True, db_index=True)
    # consent_sign = ImageField(validators=[validate_image_file_extension], blank=True)
    consent = models.BooleanField(null=True)
    # consent_sharing = MultiSelectField(choices=DATA_SHARING_CHOICES, default=BLANK)
    residence_status = models.CharField(max_length=254)

    # country_origin = models.ForeignKey("Country", related_name="+", blank=True, null=True, on_delete=models.PROTECT)
    # country = models.ForeignKey("Country", related_name="+", blank=True, null=True, on_delete=models.PROTECT)
    address = models.CharField(max_length=1024, blank=True)
    zip_code = models.CharField(max_length=12, blank=True, null=True)
    """location contains lowest administrative area info"""
    admin_area = models.ForeignKey("hope.Area", null=True, on_delete=models.SET_NULL, blank=True)
    admin1 = models.ForeignKey("hope.Area", null=True, on_delete=models.SET_NULL, blank=True, related_name="+")
    admin2 = models.ForeignKey("hope.Area", null=True, on_delete=models.SET_NULL, blank=True, related_name="+")
    admin3 = models.ForeignKey("hope.Area", null=True, on_delete=models.SET_NULL, blank=True, related_name="+")
    admin4 = models.ForeignKey("hope.Area", null=True, on_delete=models.SET_NULL, blank=True, related_name="+")
    geopoint = PointField(blank=True, null=True)

    size = models.PositiveIntegerField(db_index=True, null=True)
    representatives = models.ManyToManyField(
        to="Individual",
        through="IndividualRoleInHousehold",
        help_text="""This is only used to track collector (primary or secondary) of a household.
            They may still be a HOH of this household or any other household.
            Through model will contain the role (ROLE_CHOICE) they are connected with on.""",
        related_name="represented_households",
    )
    female_age_group_0_5_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_6_11_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_12_17_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_18_59_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_60_count = models.PositiveIntegerField(default=None, null=True)
    pregnant_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_0_5_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_6_11_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_12_17_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_18_59_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_60_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_0_5_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_6_11_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_12_17_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_18_59_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_60_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_0_5_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_6_11_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_12_17_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_18_59_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_60_disabled_count = models.PositiveIntegerField(default=None, null=True)
    children_count = models.PositiveIntegerField(default=None, null=True)
    male_children_count = models.PositiveIntegerField(default=None, null=True)
    female_children_count = models.PositiveIntegerField(default=None, null=True)
    children_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_children_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_children_disabled_count = models.PositiveIntegerField(default=None, null=True)

    # registration_data_import = models.ForeignKey(
    #     "registration_data.RegistrationDataImport",
    #     related_name="households",
    #     blank=True,
    #     null=True,
    #     on_delete=models.CASCADE,
    # )
    # programs = models.ManyToManyField(
    #     "program.Program",
    #     related_name="households",
    #     blank=True,
    # )
    returnee = models.BooleanField(null=True)
    flex_fields = JSONField(default=dict, blank=True)
    first_registration_date = models.DateTimeField()
    last_registration_date = models.DateTimeField()
    head_of_household = models.OneToOneField("Individual", related_name="heading_household", on_delete=models.CASCADE)
    fchild_hoh = models.BooleanField(null=True)
    child_hoh = models.BooleanField(null=True)
    start = models.DateTimeField(blank=True, null=True)
    deviceid = models.CharField(max_length=250, blank=True)
    name_enumerator = models.CharField(max_length=250, blank=True)
    org_enumerator = models.CharField(max_length=250)
    org_name_enumerator = models.CharField(max_length=250, blank=True)
    village = models.CharField(max_length=250, blank=True)
    registration_method = models.CharField(max_length=250)
    collect_individual_data = models.CharField(max_length=250)
    currency = models.CharField(max_length=250)
    unhcr_id = models.CharField(max_length=250, blank=True, db_index=True)
    user_fields = JSONField(default=dict, blank=True)
    kobo_asset_id = models.CharField(max_length=150, blank=True, db_index=True)
    row_id = models.PositiveIntegerField(blank=True, null=True)
    total_cash_received_usd = models.DecimalField(null=True, decimal_places=2, max_digits=64, blank=True)
    total_cash_received = models.DecimalField(null=True, decimal_places=2, max_digits=64, blank=True)

    family_id = models.CharField(max_length=100, blank=True, null=True)  # eDopomoga household id

    # storage_obj = models.ForeignKey(StorageFile, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = "household_household"
        ordering = ("unicef_id",)

    class Tenant:
        tenant_filter_field = "business_area"

    def __str__(self) -> str:
        return str(self.unicef_id)
