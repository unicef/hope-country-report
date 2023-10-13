from django.contrib.gis.db.models import PointField
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models import JSONField

from ._base import HopeModel
from .ba import BusinessArea


class Household(HopeModel):
    business_area = models.ForeignKey(BusinessArea, on_delete=models.CASCADE)
    unicef_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    id = models.CharField(primary_key=True, max_length=100, editable=False)
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

    class Tenant:
        tenant_filter_field = "business_area"

    def __str__(self):
        return self.unicef_id


class Individual(HopeModel):
    id = models.CharField(primary_key=True, max_length=100, editable=False)
    unicef_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    full_name = models.CharField(max_length=255, db_index=True)
    given_name = models.CharField(max_length=85, blank=True, db_index=True)
    middle_name = models.CharField(max_length=85, blank=True, db_index=True)
    family_name = models.CharField(max_length=85, blank=True, db_index=True)
    relationship = models.CharField(
        max_length=255,
        blank=True,
        help_text="""This represents the MEMBER relationship. can be blank
            as well if household is null!""",
    )
    household = models.ForeignKey(
        "Household",
        related_name="individuals",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="""This represents the household this person is a MEMBER,
            and if null then relationship is NON_BENEFICIARY and that
            simply means they are a representative of one or more households
            and not a member of one.""",
    )

    # registration_data_import = models.ForeignKey(
    #     "registration_data.RegistrationDataImport",
    #     related_name="individuals",
    #     on_delete=models.CASCADE,
    #     null=True,
    # )
    disability = models.CharField(max_length=20)
    work_status = models.CharField(max_length=20, blank=True)
    first_registration_date = models.DateField()
    last_registration_date = models.DateField()
    flex_fields = JSONField(default=dict, blank=True)
    user_fields = JSONField(default=dict, blank=True)
    enrolled_in_nutrition_programme = models.BooleanField(null=True)
    administration_of_rutf = models.BooleanField(null=True)
    deduplication_golden_record_status = models.CharField(max_length=50, db_index=True)
    deduplication_batch_status = models.CharField(max_length=50, db_index=True)
    deduplication_golden_record_results = JSONField(default=dict, blank=True)
    deduplication_batch_results = JSONField(default=dict, blank=True)
    imported_individual_id = models.UUIDField(null=True, blank=True)
    sanction_list_possible_match = models.BooleanField(default=False, db_index=True)
    sanction_list_confirmed_match = models.BooleanField(default=False, db_index=True)
    pregnant = models.BooleanField(null=True)
    # observed_disability = MultiSelectField(choices=OBSERVED_DISABILITY_CHOICE, default=NONE)
    seeing_disability = models.CharField(max_length=50, blank=True)
    hearing_disability = models.CharField(max_length=50, blank=True)
    physical_disability = models.CharField(max_length=50, blank=True)
    memory_disability = models.CharField(max_length=50, blank=True)
    selfcare_disability = models.CharField(max_length=50, blank=True)
    comms_disability = models.CharField(max_length=50, blank=True)
    who_answers_phone = models.CharField(max_length=150, blank=True)
    who_answers_alt_phone = models.CharField(max_length=150, blank=True)
    business_area = models.ForeignKey("BusinessArea", on_delete=models.CASCADE)
    fchild_hoh = models.BooleanField(default=False)
    child_hoh = models.BooleanField(default=False)
    kobo_asset_id = models.CharField(max_length=150, blank=True)
    row_id = models.PositiveIntegerField(blank=True, null=True)
    # disability_certificate_picture = models.ImageField(blank=True, null=True)
    preferred_language = models.CharField(max_length=6, null=True, blank=True)
    relationship_confirmed = models.BooleanField(default=False)

    vector_column = SearchVectorField(null=True)

    class Meta:
        db_table = "household_individual"

    class Tenant:
        tenant_filter_field = "business_area"


class IndividualRoleInHousehold(HopeModel):
    individual = models.ForeignKey(Individual, on_delete=models.CASCADE, related_name="households_and_roles")
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="individuals_and_roles")
    role = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("role", "household")
        db_table = "household_individualroleinhousehold"

    class Tenant:
        tenant_filter_field = "household__business_area"

    def __str__(self) -> str:
        return f"{self.individual.full_name} - {self.role}"
