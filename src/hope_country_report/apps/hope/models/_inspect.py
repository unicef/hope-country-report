# flake8: noqa F405.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
# DO NOT rename the models, AND don't rename db_table values or field names.
import django.contrib.postgres.fields
from django.contrib.gis.db import models

from hope_country_report.apps.hope.models._base import HopeModel


class BusinessArea(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    code = models.CharField(unique=True, max_length=10, null=True)
    name = models.CharField(max_length=255, null=True)
    long_name = models.CharField(max_length=255, null=True)
    region_code = models.CharField(max_length=8, null=True)
    region_name = models.CharField(max_length=8, null=True)
    kobo_username = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(unique=True, max_length=250, null=True)
    rapid_pro_payment_verification_token = models.CharField(max_length=40, blank=True, null=True)
    rapid_pro_host = models.CharField(max_length=200, blank=True, null=True)
    has_data_sharing_agreement = models.BooleanField(null=True)
    is_split = models.BooleanField(null=True)
    parent = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="businessarea_parent", blank=True, null=True
    )
    deduplication_duplicate_score = models.FloatField(null=True)
    deduplication_batch_duplicates_allowed = models.IntegerField(null=True)
    deduplication_batch_duplicates_percentage = models.IntegerField(null=True)
    deduplication_golden_record_duplicates_allowed = models.IntegerField(null=True)
    deduplication_golden_record_duplicates_percentage = models.IntegerField(null=True)
    custom_fields = models.JSONField(null=True)
    deduplication_possible_duplicate_score = models.FloatField(null=True)
    screen_beneficiary = models.BooleanField(null=True)
    postpone_deduplication = models.BooleanField(null=True)
    deduplication_ignore_withdraw = models.BooleanField(null=True)
    active = models.BooleanField(null=True)
    kobo_token = models.CharField(max_length=255, blank=True, null=True)
    kobo_url = models.CharField(max_length=255, blank=True, null=True)
    is_payment_plan_applicable = models.BooleanField(null=True)
    is_accountability_applicable = models.BooleanField(null=True)
    rapid_pro_messages_token = models.CharField(max_length=40, blank=True, null=True)
    rapid_pro_survey_token = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "core_businessarea"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)


class BusinessareaCountries(HopeModel):
    businessarea = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="businessareacountries_businessarea", null=True
    )
    country = models.ForeignKey(
        "Country", on_delete=models.DO_NOTHING, related_name="businessareacountries_country", null=True
    )

    class Meta:
        managed = False
        db_table = "core_businessarea_countries"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Countrycodemap(HopeModel):
    id = models.BigAutoField(primary_key=True)
    ca_code = models.CharField(unique=True, max_length=5, null=True)
    country = models.OneToOneField(
        "Country", on_delete=models.DO_NOTHING, related_name="countrycodemap_country", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "core_countrycodemap"

    class Tenant:
        tenant_filter_field: str = "__all__"


class DataCollectingType(HopeModel):
    id = models.BigAutoField(primary_key=True)
    created = models.DateTimeField(null=True)
    modified = models.DateTimeField(null=True)
    code = models.CharField(unique=True, max_length=60, null=True)
    description = models.TextField(null=True)

    class Meta:
        managed = False
        db_table = "core_datacollectingtype"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.code)


class DatacollectingtypeCompatibleTypes(HopeModel):
    id = models.BigAutoField(primary_key=True)
    from_datacollectingtype = models.ForeignKey(
        DataCollectingType,
        on_delete=models.DO_NOTHING,
        related_name="datacollectingtypecompatibletypes_from_datacollectingtype",
        null=True,
    )
    to_datacollectingtype = models.ForeignKey(
        DataCollectingType,
        on_delete=models.DO_NOTHING,
        related_name="datacollectingtypecompatibletypes_to_datacollectingtype",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "core_datacollectingtype_compatible_types"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Area(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    original_id = models.UUIDField(blank=True, null=True)
    name = models.CharField(max_length=255, null=True)
    p_code = models.CharField(max_length=32, blank=True, null=True)
    geom = models.GeometryField(blank=True, null=True)
    point = models.GeometryField(blank=True, null=True)
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    extras = models.JSONField(null=True)
    lft = models.IntegerField(null=True)
    rght = models.IntegerField(null=True)
    tree_id = models.IntegerField(null=True)
    level = models.IntegerField(null=True)
    area_type = models.ForeignKey("Areatype", on_delete=models.DO_NOTHING, related_name="area_area_type", null=True)
    parent = models.ForeignKey("self", on_delete=models.DO_NOTHING, related_name="area_parent", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "geo_area"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)


class Areatype(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    original_id = models.UUIDField(blank=True, null=True)
    name = models.TextField(null=True)  # This field type is a guess.
    area_level = models.IntegerField(null=True)
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    extras = models.JSONField(null=True)
    lft = models.IntegerField(null=True)
    rght = models.IntegerField(null=True)
    tree_id = models.IntegerField(null=True)
    level = models.IntegerField(null=True)
    country = models.ForeignKey("Country", on_delete=models.DO_NOTHING, related_name="areatype_country", null=True)
    parent = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="areatype_parent", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "geo_areatype"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)


class Country(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    original_id = models.UUIDField(blank=True, null=True)
    name = models.TextField(null=True)  # This field type is a guess.
    short_name = models.TextField(null=True)  # This field type is a guess.
    iso_code2 = models.CharField(unique=True, max_length=2, null=True)
    iso_code3 = models.CharField(unique=True, max_length=3, null=True)
    iso_num = models.CharField(unique=True, max_length=4, null=True)
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    extras = models.JSONField(null=True)
    lft = models.IntegerField(null=True)
    rght = models.IntegerField(null=True)
    tree_id = models.IntegerField(null=True)
    level = models.IntegerField(null=True)
    parent = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="country_parent", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "geo_country"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)


class BankaccountInfo(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    is_removed = models.BooleanField(null=True)
    removed_date = models.DateTimeField(blank=True, null=True)
    last_sync_at = models.DateTimeField(blank=True, null=True)
    bank_name = models.CharField(max_length=255, null=True)
    bank_account_number = models.CharField(max_length=64, null=True)
    debit_card_number = models.CharField(max_length=255, null=True)
    individual = models.ForeignKey(
        "Individual", on_delete=models.DO_NOTHING, related_name="bankaccountinfo_individual", null=True
    )
    copied_from = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="bankaccountinfo_copied_from", blank=True, null=True
    )
    is_migration_handled = models.BooleanField(null=True)
    is_original = models.BooleanField(null=True)

    class Meta:
        managed = False
        db_table = "household_bankaccountinfo"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Document(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    document_number = models.CharField(max_length=255, null=True)
    photo = models.CharField(max_length=100, null=True)
    individual = models.ForeignKey(
        "Individual", on_delete=models.DO_NOTHING, related_name="document_individual", null=True
    )
    type = models.ForeignKey("DocumentType", on_delete=models.DO_NOTHING, related_name="document_type", null=True)
    is_removed = models.BooleanField(null=True)
    status = models.CharField(max_length=20, null=True)
    country = models.ForeignKey(
        Country, on_delete=models.DO_NOTHING, related_name="document_country", blank=True, null=True
    )
    last_sync_at = models.DateTimeField(blank=True, null=True)
    cleared = models.BooleanField(null=True)
    cleared_date = models.DateTimeField(null=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    issuance_date = models.DateTimeField(blank=True, null=True)
    copied_from = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="document_copied_from", blank=True, null=True
    )
    is_migration_handled = models.BooleanField(null=True)
    is_original = models.BooleanField(null=True)
    program = models.ForeignKey(
        "Program", on_delete=models.DO_NOTHING, related_name="document_program", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "household_document"

    class Tenant:
        tenant_filter_field: str = "__all__"


class DocumentType(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    label = models.CharField(max_length=100, null=True)
    key = models.CharField(unique=True, max_length=50, null=True)
    is_identity_document = models.BooleanField(null=True)
    unique_for_individual = models.BooleanField(null=True)
    valid_for_deduplication = models.BooleanField(null=True)

    class Meta:
        managed = False
        db_table = "household_documenttype"

    class Tenant:
        tenant_filter_field: str = "__all__"


class DocumentValidator(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    regex = models.CharField(max_length=100, null=True)
    type = models.ForeignKey(
        DocumentType, on_delete=models.DO_NOTHING, related_name="documentvalidator_type", null=True
    )

    class Meta:
        managed = False
        db_table = "household_documentvalidator"

    class Tenant:
        tenant_filter_field: str = "__all__"


class EntitlementCard(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    card_number = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=10, null=True)
    card_type = models.CharField(max_length=255, null=True)
    current_card_size = models.CharField(max_length=255, null=True)
    card_custodian = models.CharField(max_length=255, null=True)
    service_provider = models.CharField(max_length=255, null=True)
    household = models.ForeignKey(
        "Household", on_delete=models.DO_NOTHING, related_name="entitlementcard_household", blank=True, null=True
    )
    is_original = models.BooleanField(null=True)

    class Meta:
        managed = False
        db_table = "household_entitlementcard"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Household(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    residence_status = models.CharField(max_length=254, null=True)
    size = models.IntegerField(blank=True, null=True)
    address = models.TextField(null=True)  # This field type is a guess.
    geopoint = models.GeometryField(blank=True, null=True)
    female_age_group_0_5_count = models.IntegerField(blank=True, null=True)
    female_age_group_6_11_count = models.IntegerField(blank=True, null=True)
    female_age_group_12_17_count = models.IntegerField(blank=True, null=True)
    pregnant_count = models.IntegerField(blank=True, null=True)
    male_age_group_0_5_count = models.IntegerField(blank=True, null=True)
    male_age_group_6_11_count = models.IntegerField(blank=True, null=True)
    male_age_group_12_17_count = models.IntegerField(blank=True, null=True)
    female_age_group_0_5_disabled_count = models.IntegerField(blank=True, null=True)
    female_age_group_6_11_disabled_count = models.IntegerField(blank=True, null=True)
    female_age_group_12_17_disabled_count = models.IntegerField(blank=True, null=True)
    male_age_group_0_5_disabled_count = models.IntegerField(blank=True, null=True)
    male_age_group_6_11_disabled_count = models.IntegerField(blank=True, null=True)
    male_age_group_12_17_disabled_count = models.IntegerField(blank=True, null=True)
    returnee = models.BooleanField(blank=True, null=True)
    flex_fields = models.JSONField(null=True)
    head_of_household = models.OneToOneField(
        "Individual", on_delete=models.DO_NOTHING, related_name="household_head_of_household", null=True
    )
    last_sync_at = models.DateTimeField(blank=True, null=True)
    first_registration_date = models.DateTimeField(null=True)
    last_registration_date = models.DateTimeField(null=True)
    unicef_id = models.CharField(max_length=255, blank=True, null=True)
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="household_business_area", null=True
    )
    child_hoh = models.BooleanField(blank=True, null=True)
    consent_sharing = models.CharField(max_length=63, null=True)
    consent_sign = models.CharField(max_length=100, null=True)
    deviceid = models.CharField(max_length=250, null=True)
    fchild_hoh = models.BooleanField(blank=True, null=True)
    name_enumerator = models.CharField(max_length=250, null=True)
    org_enumerator = models.CharField(max_length=250, null=True)
    org_name_enumerator = models.CharField(max_length=250, null=True)
    start = models.DateTimeField(blank=True, null=True)
    village = models.CharField(max_length=250, null=True)
    consent = models.BooleanField(blank=True, null=True)
    is_removed = models.BooleanField(null=True)
    collect_individual_data = models.CharField(max_length=250, null=True)
    currency = models.CharField(max_length=250, null=True)
    female_age_group_18_59_count = models.IntegerField(blank=True, null=True)
    female_age_group_18_59_disabled_count = models.IntegerField(blank=True, null=True)
    female_age_group_60_count = models.IntegerField(blank=True, null=True)
    female_age_group_60_disabled_count = models.IntegerField(blank=True, null=True)
    male_age_group_18_59_count = models.IntegerField(blank=True, null=True)
    male_age_group_18_59_disabled_count = models.IntegerField(blank=True, null=True)
    male_age_group_60_count = models.IntegerField(blank=True, null=True)
    male_age_group_60_disabled_count = models.IntegerField(blank=True, null=True)
    registration_method = models.CharField(max_length=250, null=True)
    unhcr_id = models.CharField(max_length=250, null=True)
    version = models.BigIntegerField(null=True)
    withdrawn = models.BooleanField(null=True)
    withdrawn_date = models.DateTimeField(blank=True, null=True)
    removed_date = models.DateTimeField(blank=True, null=True)
    user_fields = models.JSONField(null=True)
    country = models.ForeignKey(
        Country, on_delete=models.DO_NOTHING, related_name="household_country", blank=True, null=True
    )
    country_origin = models.ForeignKey(
        Country, on_delete=models.DO_NOTHING, related_name="household_country_origin", blank=True, null=True
    )
    admin_area = models.ForeignKey(
        Area, on_delete=models.DO_NOTHING, related_name="household_admin_area", blank=True, null=True
    )
    kobo_asset_id = models.CharField(max_length=150, null=True)
    row_id = models.IntegerField(blank=True, null=True)
    children_count = models.IntegerField(blank=True, null=True)
    children_disabled_count = models.IntegerField(blank=True, null=True)
    female_children_count = models.IntegerField(blank=True, null=True)
    female_children_disabled_count = models.IntegerField(blank=True, null=True)
    male_children_count = models.IntegerField(blank=True, null=True)
    male_children_disabled_count = models.IntegerField(blank=True, null=True)
    total_cash_received = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True)
    total_cash_received_usd = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True)
    family_id = models.CharField(max_length=100, blank=True, null=True)
    admin1 = models.ForeignKey(
        Area, on_delete=models.DO_NOTHING, related_name="household_admin1", blank=True, null=True
    )
    admin2 = models.ForeignKey(
        Area, on_delete=models.DO_NOTHING, related_name="household_admin2", blank=True, null=True
    )
    admin3 = models.ForeignKey(
        Area, on_delete=models.DO_NOTHING, related_name="household_admin3", blank=True, null=True
    )
    admin4 = models.ForeignKey(
        Area, on_delete=models.DO_NOTHING, related_name="household_admin4", blank=True, null=True
    )
    zip_code = models.CharField(max_length=12, blank=True, null=True)
    registration_id = models.IntegerField(blank=True, null=True)
    copied_from = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="household_copied_from", blank=True, null=True
    )
    is_migration_handled = models.BooleanField(null=True)
    is_original = models.BooleanField(null=True)
    origin_unicef_id = models.CharField(max_length=100, blank=True, null=True)
    program = models.ForeignKey(
        "Program", on_delete=models.DO_NOTHING, related_name="household_program", blank=True, null=True
    )
    household_collection = models.ForeignKey(
        "Householdcollection",
        on_delete=models.DO_NOTHING,
        related_name="household_household_collection",
        blank=True,
        null=True,
    )
    data_collecting_type = models.ForeignKey(
        DataCollectingType,
        on_delete=models.DO_NOTHING,
        related_name="household_data_collecting_type",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "household_household"

    class Tenant:
        tenant_filter_field: str = "__all__"


class HouseholdPrograms(HopeModel):
    household = models.ForeignKey(
        Household, on_delete=models.DO_NOTHING, related_name="householdprograms_household", null=True
    )
    program = models.ForeignKey(
        "Program", on_delete=models.DO_NOTHING, related_name="householdprograms_program", null=True
    )

    class Meta:
        managed = False
        db_table = "household_household_programs"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Householdcollection(HopeModel):
    id = models.BigAutoField(primary_key=True)
    unicef_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "household_householdcollection"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Individual(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    individual_id = models.CharField(max_length=255, null=True)
    photo = models.CharField(max_length=100, null=True)
    full_name = models.TextField(null=True)  # This field type is a guess.
    given_name = models.TextField(null=True)  # This field type is a guess.
    middle_name = models.TextField(null=True)  # This field type is a guess.
    family_name = models.TextField(null=True)  # This field type is a guess.
    relationship = models.CharField(max_length=255, null=True)
    sex = models.CharField(max_length=255, null=True)
    birth_date = models.DateField(null=True)
    estimated_birth_date = models.BooleanField(null=True)
    marital_status = models.CharField(max_length=255, null=True)
    phone_no = models.CharField(max_length=128, null=True)
    phone_no_alternative = models.CharField(max_length=128, null=True)
    disability = models.CharField(max_length=20, null=True)
    flex_fields = models.JSONField(null=True)
    household = models.ForeignKey(
        Household, on_delete=models.DO_NOTHING, related_name="individual_household", blank=True, null=True
    )
    last_sync_at = models.DateTimeField(blank=True, null=True)
    administration_of_rutf = models.BooleanField(blank=True, null=True)
    enrolled_in_nutrition_programme = models.BooleanField(blank=True, null=True)
    work_status = models.CharField(max_length=20, null=True)
    first_registration_date = models.DateField(null=True)
    last_registration_date = models.DateField(null=True)
    unicef_id = models.CharField(max_length=255, blank=True, null=True)
    deduplication_golden_record_status = models.CharField(max_length=50, null=True)
    deduplication_golden_record_results = models.JSONField(null=True)
    sanction_list_possible_match = models.BooleanField(null=True)
    pregnant = models.BooleanField(blank=True, null=True)
    deduplication_batch_results = models.JSONField(null=True)
    deduplication_batch_status = models.CharField(max_length=50, null=True)
    imported_individual_id = models.UUIDField(blank=True, null=True)
    comms_disability = models.CharField(max_length=50, null=True)
    hearing_disability = models.CharField(max_length=50, null=True)
    memory_disability = models.CharField(max_length=50, null=True)
    observed_disability = models.CharField(max_length=58, null=True)
    physical_disability = models.CharField(max_length=50, null=True)
    seeing_disability = models.CharField(max_length=50, null=True)
    selfcare_disability = models.CharField(max_length=50, null=True)
    who_answers_alt_phone = models.CharField(max_length=150, null=True)
    who_answers_phone = models.CharField(max_length=150, null=True)
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="individual_business_area", null=True
    )
    is_removed = models.BooleanField(null=True)
    version = models.BigIntegerField(null=True)
    duplicate = models.BooleanField(null=True)
    duplicate_date = models.DateTimeField(blank=True, null=True)
    withdrawn = models.BooleanField(null=True)
    withdrawn_date = models.DateTimeField(blank=True, null=True)
    removed_date = models.DateTimeField(blank=True, null=True)
    sanction_list_confirmed_match = models.BooleanField(null=True)
    user_fields = models.JSONField(null=True)
    child_hoh = models.BooleanField(null=True)
    fchild_hoh = models.BooleanField(null=True)
    kobo_asset_id = models.CharField(max_length=150, null=True)
    row_id = models.IntegerField(blank=True, null=True)
    disability_certificate_picture = models.CharField(max_length=100, blank=True, null=True)
    vector_column = models.TextField(blank=True, null=True)  # This field type is a guess.
    phone_no_alternative_valid = models.BooleanField(blank=True, null=True)
    phone_no_valid = models.BooleanField(blank=True, null=True)
    preferred_language = models.CharField(max_length=6, blank=True, null=True)
    relationship_confirmed = models.BooleanField(null=True)
    email = models.CharField(max_length=255, null=True)
    age_at_registration = models.SmallIntegerField(blank=True, null=True)
    registration_id = models.IntegerField(blank=True, null=True)
    copied_from = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="individual_copied_from", blank=True, null=True
    )
    is_migration_handled = models.BooleanField(null=True)
    is_original = models.BooleanField(null=True)
    origin_unicef_id = models.CharField(max_length=100, blank=True, null=True)
    program = models.ForeignKey(
        "Program", on_delete=models.DO_NOTHING, related_name="individual_program", blank=True, null=True
    )
    individual_collection = models.ForeignKey(
        "Individualcollection",
        on_delete=models.DO_NOTHING,
        related_name="individual_individual_collection",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "household_individual"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Individualcollection(HopeModel):
    id = models.BigAutoField(primary_key=True)
    unicef_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "household_individualcollection"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Individualidentity(HopeModel):
    id = models.BigAutoField(primary_key=True)
    number = models.CharField(max_length=255, null=True)
    individual = models.ForeignKey(
        Individual, on_delete=models.DO_NOTHING, related_name="individualidentity_individual", null=True
    )
    country = models.ForeignKey(
        Country, on_delete=models.DO_NOTHING, related_name="individualidentity_country", blank=True, null=True
    )
    copied_from = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="individualidentity_copied_from", blank=True, null=True
    )
    created = models.DateTimeField(null=True)
    is_migration_handled = models.BooleanField(null=True)
    is_original = models.BooleanField(null=True)
    is_removed = models.BooleanField(null=True)
    modified = models.DateTimeField(null=True)

    class Meta:
        managed = False
        db_table = "household_individualidentity"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Individualroleinhousehold(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    last_sync_at = models.DateTimeField(blank=True, null=True)
    role = models.CharField(max_length=255, null=True)
    household = models.ForeignKey(
        Household, on_delete=models.DO_NOTHING, related_name="individualroleinhousehold_household", null=True
    )
    individual = models.ForeignKey(
        Individual, on_delete=models.DO_NOTHING, related_name="individualroleinhousehold_individual", null=True
    )
    copied_from = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="individualroleinhousehold_copied_from", blank=True, null=True
    )
    is_migration_handled = models.BooleanField(null=True)
    is_original = models.BooleanField(null=True)
    is_removed = models.BooleanField(null=True)

    class Meta:
        managed = False
        db_table = "household_individualroleinhousehold"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Acceptanceprocessthreshold(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    payments_range_usd = django.contrib.postgres.fields.IntegerRangeField(null=True)
    approval_number_required = models.IntegerField(null=True)
    authorization_number_required = models.IntegerField(null=True)
    finance_release_number_required = models.IntegerField(null=True)
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="acceptanceprocessthreshold_business_area", null=True
    )

    class Meta:
        managed = False
        db_table = "payment_acceptanceprocessthreshold"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Approval(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    type = models.CharField(max_length=50, null=True)
    comment = models.CharField(max_length=500, blank=True, null=True)
    approval_process = models.ForeignKey(
        "Approvalprocess", on_delete=models.DO_NOTHING, related_name="approval_approval_process", null=True
    )

    class Meta:
        managed = False
        db_table = "payment_approval"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Approvalprocess(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    sent_for_approval_date = models.DateTimeField(blank=True, null=True)
    sent_for_authorization_date = models.DateTimeField(blank=True, null=True)
    sent_for_finance_release_date = models.DateTimeField(blank=True, null=True)
    payment_plan = models.ForeignKey(
        "PaymentPlan", on_delete=models.DO_NOTHING, related_name="approvalprocess_payment_plan", null=True
    )
    approval_number_required = models.IntegerField(null=True)
    authorization_number_required = models.IntegerField(null=True)
    finance_release_number_required = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = "payment_approvalprocess"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Cashplan(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    ca_id = models.CharField(max_length=255, blank=True, null=True)
    ca_hash_id = models.UUIDField(unique=True, blank=True, null=True)
    status = models.CharField(max_length=255, null=True)
    status_date = models.DateTimeField(null=True)
    name = models.CharField(max_length=255, null=True)
    distribution_level = models.CharField(max_length=255, null=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    dispersion_date = models.DateTimeField(null=True)
    coverage_duration = models.IntegerField(null=True)
    coverage_unit = models.CharField(max_length=255, null=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    delivery_type = models.CharField(max_length=24, blank=True, null=True)
    assistance_measurement = models.CharField(max_length=255, null=True)
    assistance_through = models.CharField(max_length=255, null=True)
    vision_id = models.CharField(max_length=255, blank=True, null=True)
    funds_commitment = models.CharField(max_length=255, blank=True, null=True)
    down_payment = models.CharField(max_length=255, blank=True, null=True)
    validation_alerts_count = models.IntegerField(null=True)
    total_persons_covered = models.IntegerField(null=True)
    total_persons_covered_revised = models.IntegerField(null=True)
    total_entitled_quantity = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_entitled_quantity_revised = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_delivered_quantity = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_undelivered_quantity = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="cashplan_business_area", null=True
    )
    program = models.ForeignKey("Program", on_delete=models.DO_NOTHING, related_name="cashplan_program", null=True)
    exchange_rate = models.DecimalField(max_digits=14, decimal_places=8, blank=True, null=True)
    service_provider = models.ForeignKey(
        "Serviceprovider", on_delete=models.DO_NOTHING, related_name="cashplan_service_provider", blank=True, null=True
    )
    total_delivered_quantity_usd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_entitled_quantity_revised_usd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_entitled_quantity_usd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_undelivered_quantity_usd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    version = models.BigIntegerField(null=True)

    class Meta:
        managed = False
        db_table = "payment_cashplan"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)


class Deliverymechanismperpaymentplan(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    sent_date = models.DateTimeField(null=True)
    status = models.CharField(max_length=50, null=True)
    delivery_mechanism_order = models.IntegerField(null=True)
    delivery_mechanism = models.CharField(max_length=255, blank=True, null=True)
    payment_plan = models.ForeignKey(
        "PaymentPlan",
        on_delete=models.DO_NOTHING,
        related_name="deliverymechanismperpaymentplan_payment_plan",
        null=True,
    )
    financial_service_provider = models.ForeignKey(
        "Financialserviceprovider",
        on_delete=models.DO_NOTHING,
        related_name="deliverymechanismperpaymentplan_financial_service_provider",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "payment_deliverymechanismperpaymentplan"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Financialserviceprovider(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    name = models.CharField(unique=True, max_length=100, null=True)
    vision_vendor_number = models.CharField(unique=True, max_length=100, null=True)
    delivery_mechanisms = models.TextField(null=True)  # This field type is a guess.
    distribution_limit = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    communication_channel = models.CharField(max_length=6, null=True)
    data_transfer_configuration = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "payment_financialserviceprovider"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)


class Financialserviceproviderxlsxreport(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    file = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    financial_service_provider = models.ForeignKey(
        Financialserviceprovider,
        on_delete=models.DO_NOTHING,
        related_name="financialserviceproviderxlsxreport_financial_service_provider",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "payment_financialserviceproviderxlsxreport"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Financialserviceproviderxlsxtemplate(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    name = models.CharField(max_length=120, null=True)
    columns = models.CharField(max_length=500, null=True)
    core_fields = models.TextField(null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "payment_financialserviceproviderxlsxtemplate"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)


class Fspxlsxtemplateperdeliverymechanism(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    delivery_mechanism = models.CharField(max_length=255, null=True)
    financial_service_provider = models.ForeignKey(
        Financialserviceprovider,
        on_delete=models.DO_NOTHING,
        related_name="fspxlsxtemplateperdeliverymechanism_financial_service_provider",
        null=True,
    )
    xlsx_template = models.ForeignKey(
        Financialserviceproviderxlsxtemplate,
        on_delete=models.DO_NOTHING,
        related_name="fspxlsxtemplateperdeliverymechanism_xlsx_template",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "payment_fspxlsxtemplateperdeliverymechanism"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Payment(HopeModel):
    is_removed = models.BooleanField(null=True)
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=255, null=True)
    status_date = models.DateTimeField(null=True)
    delivery_type = models.CharField(max_length=24, blank=True, null=True)
    currency = models.CharField(max_length=4, null=True)
    entitlement_quantity = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    entitlement_quantity_usd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    delivered_quantity = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    delivered_quantity_usd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    delivery_date = models.DateTimeField(blank=True, null=True)
    transaction_reference_id = models.CharField(max_length=255, blank=True, null=True)
    excluded = models.BooleanField(null=True)
    entitlement_date = models.DateTimeField(blank=True, null=True)
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="payment_business_area", null=True
    )
    head_of_household = models.ForeignKey(
        Individual, on_delete=models.DO_NOTHING, related_name="payment_head_of_household", blank=True, null=True
    )
    household = models.ForeignKey(Household, on_delete=models.DO_NOTHING, related_name="payment_household", null=True)
    parent = models.ForeignKey("PaymentPlan", on_delete=models.DO_NOTHING, related_name="payment_parent", null=True)
    financial_service_provider = models.ForeignKey(
        Financialserviceprovider,
        on_delete=models.DO_NOTHING,
        related_name="payment_financial_service_provider",
        blank=True,
        null=True,
    )
    collector = models.ForeignKey(Individual, on_delete=models.DO_NOTHING, related_name="payment_collector", null=True)
    unicef_id = models.CharField(max_length=255, blank=True, null=True)
    conflicted = models.BooleanField(null=True)
    is_follow_up = models.BooleanField(null=True)
    source_payment = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="payment_source_payment", blank=True, null=True
    )
    reason_for_unsuccessful_payment = models.CharField(max_length=255, blank=True, null=True)
    order_number = models.IntegerField(blank=True, null=True)
    program = models.ForeignKey(
        "Program", on_delete=models.DO_NOTHING, related_name="payment_program", blank=True, null=True
    )
    token_number = models.IntegerField(blank=True, null=True)
    copied_from = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="payment_copied_from", blank=True, null=True
    )
    is_migration_handled = models.BooleanField(null=True)
    is_original = models.BooleanField(null=True)

    class Meta:
        managed = False
        db_table = "payment_payment"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Paymenthouseholdsnapshot(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    snapshot_data = models.JSONField(null=True)
    household_id = models.UUIDField(null=True)
    payment = models.OneToOneField(
        Payment, on_delete=models.DO_NOTHING, related_name="paymenthouseholdsnapshot_payment", null=True
    )

    class Meta:
        managed = False
        db_table = "payment_paymenthouseholdsnapshot"

    class Tenant:
        tenant_filter_field: str = "__all__"


class PaymentPlan(HopeModel):
    is_removed = models.BooleanField(null=True)
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    status_date = models.DateTimeField(null=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    exchange_rate = models.DecimalField(max_digits=14, decimal_places=8, blank=True, null=True)
    total_entitled_quantity = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_entitled_quantity_usd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_entitled_quantity_revised = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_entitled_quantity_revised_usd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_delivered_quantity = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_delivered_quantity_usd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_undelivered_quantity = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_undelivered_quantity_usd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=50, null=True)
    unicef_id = models.CharField(max_length=255, blank=True, null=True)
    currency = models.CharField(max_length=4, null=True)
    dispersion_start_date = models.DateField(null=True)
    dispersion_end_date = models.DateField(null=True)
    female_children_count = models.IntegerField(null=True)
    male_children_count = models.IntegerField(null=True)
    female_adults_count = models.IntegerField(null=True)
    male_adults_count = models.IntegerField(null=True)
    total_households_count = models.IntegerField(null=True)
    total_individuals_count = models.IntegerField(null=True)
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="paymentplan_business_area", null=True
    )
    program = models.ForeignKey("Program", on_delete=models.DO_NOTHING, related_name="paymentplan_program", null=True)
    target_population = models.ForeignKey(
        "Targetpopulation", on_delete=models.DO_NOTHING, related_name="paymentplan_target_population", null=True
    )
    steficon_applied_date = models.DateTimeField(blank=True, null=True)
    imported_file_date = models.DateTimeField(blank=True, null=True)
    background_action_status = models.CharField(max_length=50, blank=True, null=True)
    is_follow_up = models.BooleanField(null=True)
    program_cycle = models.ForeignKey(
        "ProgramCycle", on_delete=models.DO_NOTHING, related_name="paymentplan_program_cycle", blank=True, null=True
    )
    source_payment_plan = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="paymentplan_source_payment_plan", blank=True, null=True
    )
    exclusion_reason = models.TextField(null=True)
    exclude_household_error = models.TextField(null=True)
    version = models.BigIntegerField(null=True)

    class Meta:
        managed = False
        db_table = "payment_paymentplan"

    class Tenant:
        tenant_filter_field: str = "__all__"


class PaymentRecord(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=255, null=True)
    status_date = models.DateTimeField(null=True)
    ca_id = models.CharField(max_length=255, blank=True, null=True)
    ca_hash_id = models.UUIDField(unique=True, blank=True, null=True)
    full_name = models.CharField(max_length=255, null=True)
    total_persons_covered = models.IntegerField(null=True)
    distribution_modality = models.CharField(max_length=255, null=True)
    target_population_cash_assist_id = models.CharField(max_length=255, null=True)
    entitlement_card_number = models.CharField(max_length=255, blank=True, null=True)
    entitlement_card_status = models.CharField(max_length=20, blank=True, null=True)
    entitlement_card_issue_date = models.DateField(blank=True, null=True)
    delivery_type = models.CharField(max_length=24, blank=True, null=True)
    currency = models.CharField(max_length=4, null=True)
    entitlement_quantity = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    delivered_quantity = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    delivery_date = models.DateTimeField(blank=True, null=True)
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="paymentrecord_business_area", null=True
    )
    parent = models.ForeignKey(
        Cashplan, on_delete=models.DO_NOTHING, related_name="paymentrecord_parent", blank=True, null=True
    )
    household = models.ForeignKey(
        Household, on_delete=models.DO_NOTHING, related_name="paymentrecord_household", null=True
    )
    service_provider = models.ForeignKey(
        "Serviceprovider", on_delete=models.DO_NOTHING, related_name="paymentrecord_service_provider", null=True
    )
    target_population = models.ForeignKey(
        "Targetpopulation", on_delete=models.DO_NOTHING, related_name="paymentrecord_target_population", null=True
    )
    transaction_reference_id = models.CharField(max_length=255, blank=True, null=True)
    vision_id = models.CharField(max_length=255, blank=True, null=True)
    version = models.BigIntegerField(null=True)
    delivered_quantity_usd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    head_of_household = models.ForeignKey(
        Individual, on_delete=models.DO_NOTHING, related_name="paymentrecord_head_of_household", blank=True, null=True
    )
    registration_ca_id = models.CharField(max_length=255, blank=True, null=True)
    entitlement_quantity_usd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    copied_from = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="paymentrecord_copied_from", blank=True, null=True
    )
    is_migration_handled = models.BooleanField(null=True)
    is_original = models.BooleanField(null=True)

    class Meta:
        managed = False
        db_table = "payment_paymentrecord"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Paymentverification(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=50, null=True)
    status_date = models.DateTimeField(blank=True, null=True)
    payment_verification_plan = models.ForeignKey(
        "Paymentverificationplan",
        on_delete=models.DO_NOTHING,
        related_name="paymentverification_payment_verification_plan",
        null=True,
    )
    received_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    version = models.BigIntegerField(null=True)
    sent_to_rapid_pro = models.BooleanField(null=True)
    payment_object_id = models.UUIDField(null=True)

    class Meta:
        managed = False
        db_table = "payment_paymentverification"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Paymentverificationplan(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=50, null=True)
    sampling = models.CharField(max_length=50, null=True)
    verification_channel = models.CharField(max_length=50, null=True)
    sample_size = models.IntegerField(blank=True, null=True)
    responded_count = models.IntegerField(blank=True, null=True)
    received_count = models.IntegerField(blank=True, null=True)
    not_received_count = models.IntegerField(blank=True, null=True)
    received_with_problems_count = models.IntegerField(blank=True, null=True)
    confidence_interval = models.FloatField(blank=True, null=True)
    margin_of_error = models.FloatField(blank=True, null=True)
    rapid_pro_flow_id = models.CharField(max_length=255, null=True)
    age_filter = models.JSONField(blank=True, null=True)
    excluded_admin_areas_filter = models.JSONField(blank=True, null=True)
    sex_filter = models.CharField(max_length=10, blank=True, null=True)
    activation_date = models.DateTimeField(blank=True, null=True)
    completion_date = models.DateTimeField(blank=True, null=True)
    version = models.BigIntegerField(null=True)
    unicef_id = models.CharField(max_length=255, blank=True, null=True)
    rapid_pro_flow_start_uuids = models.TextField(null=True)  # This field type is a guess.
    xlsx_file_exporting = models.BooleanField(null=True)
    xlsx_file_imported = models.BooleanField(null=True)
    error = models.CharField(max_length=500, blank=True, null=True)
    payment_plan_object_id = models.UUIDField(null=True)

    class Meta:
        managed = False
        db_table = "payment_paymentverificationplan"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Paymentverificationsummary(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=50, null=True)
    activation_date = models.DateTimeField(blank=True, null=True)
    completion_date = models.DateTimeField(blank=True, null=True)
    payment_plan_object_id = models.UUIDField(null=True)

    class Meta:
        managed = False
        db_table = "payment_paymentverificationsummary"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Serviceprovider(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    ca_id = models.CharField(unique=True, max_length=255, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    short_name = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=3, null=True)
    vision_id = models.CharField(max_length=255, blank=True, null=True)
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="serviceprovider_business_area", null=True
    )

    class Meta:
        managed = False
        db_table = "payment_serviceprovider"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Program(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    name = models.TextField(null=True)  # This field type is a guess.
    status = models.CharField(max_length=10, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    description = models.CharField(max_length=255, null=True)
    budget = models.DecimalField(max_digits=11, decimal_places=2, null=True)
    frequency_of_payments = models.CharField(max_length=50, null=True)
    sector = models.CharField(max_length=50, null=True)
    scope = models.CharField(max_length=50, null=True)
    cash_plus = models.BooleanField(null=True)
    population_goal = models.IntegerField(null=True)
    administrative_areas_of_implementation = models.CharField(max_length=255, null=True)
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="program_business_area", null=True
    )
    last_sync_at = models.DateTimeField(blank=True, null=True)
    ca_hash_id = models.TextField(blank=True, null=True)  # This field type is a guess.
    ca_id = models.TextField(blank=True, null=True)  # This field type is a guess.
    individual_data_needed = models.BooleanField(null=True)
    is_removed = models.BooleanField(null=True)
    version = models.BigIntegerField(null=True)
    data_collecting_type = models.ForeignKey(
        DataCollectingType,
        on_delete=models.DO_NOTHING,
        related_name="program_data_collecting_type",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "program_program"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)


class ProgramAdminAreas(HopeModel):
    program = models.ForeignKey(
        Program, on_delete=models.DO_NOTHING, related_name="programadminareas_program", null=True
    )
    area = models.ForeignKey(Area, on_delete=models.DO_NOTHING, related_name="programadminareas_area", null=True)

    class Meta:
        managed = False
        db_table = "program_program_admin_areas"

    class Tenant:
        tenant_filter_field: str = "__all__"


class ProgramCycle(HopeModel):
    is_removed = models.BooleanField(null=True)
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    last_sync_at = models.DateTimeField(blank=True, null=True)
    version = models.BigIntegerField(null=True)
    iteration = models.IntegerField(null=True)
    status = models.CharField(max_length=10, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=255, null=True)
    program = models.ForeignKey(Program, on_delete=models.DO_NOTHING, related_name="programcycle_program", null=True)

    class Meta:
        managed = False
        db_table = "program_programcycle"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.description)


class Householdselection(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    vulnerability_score = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    household = models.ForeignKey(
        Household, on_delete=models.DO_NOTHING, related_name="householdselection_household", null=True
    )
    target_population = models.ForeignKey(
        "Targetpopulation", on_delete=models.DO_NOTHING, related_name="householdselection_target_population", null=True
    )
    is_migration_handled = models.BooleanField(null=True)
    is_original = models.BooleanField(null=True)

    class Meta:
        managed = False
        db_table = "targeting_householdselection"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Targetingcriteria(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    flag_exclude_if_active_adjudication_ticket = models.BooleanField(null=True)
    flag_exclude_if_on_sanction_list = models.BooleanField(null=True)

    class Meta:
        managed = False
        db_table = "targeting_targetingcriteria"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Targetingcriteriarule(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    targeting_criteria = models.ForeignKey(
        Targetingcriteria,
        on_delete=models.DO_NOTHING,
        related_name="targetingcriteriarule_targeting_criteria",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "targeting_targetingcriteriarule"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Targetingcriteriarulefilter(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    comparison_method = models.CharField(max_length=20, null=True)
    is_flex_field = models.BooleanField(null=True)
    field_name = models.CharField(max_length=50, null=True)
    arguments = models.JSONField(null=True)
    targeting_criteria_rule = models.ForeignKey(
        Targetingcriteriarule,
        on_delete=models.DO_NOTHING,
        related_name="targetingcriteriarulefilter_targeting_criteria_rule",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "targeting_targetingcriteriarulefilter"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Targetingindividualblockrulefilter(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    comparison_method = models.CharField(max_length=20, null=True)
    is_flex_field = models.BooleanField(null=True)
    field_name = models.CharField(max_length=50, null=True)
    arguments = models.JSONField(null=True)
    individuals_filters_block = models.ForeignKey(
        "Targetingindividualrulefilterblock",
        on_delete=models.DO_NOTHING,
        related_name="targetingindividualblockrulefilter_individuals_filters_block",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "targeting_targetingindividualblockrulefilter"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Targetingindividualrulefilterblock(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    targeting_criteria_rule = models.ForeignKey(
        Targetingcriteriarule,
        on_delete=models.DO_NOTHING,
        related_name="targetingindividualrulefilterblock_targeting_criteria_rule",
        null=True,
    )
    target_only_hoh = models.BooleanField(null=True)

    class Meta:
        managed = False
        db_table = "targeting_targetingindividualrulefilterblock"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Targetpopulation(HopeModel):
    is_removed = models.BooleanField(null=True)
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    name = models.TextField(unique=True, null=True)  # This field type is a guess.
    status = models.CharField(max_length=256, null=True)
    total_households_count = models.IntegerField(blank=True, null=True)
    total_individuals_count = models.IntegerField(blank=True, null=True)
    targeting_criteria = models.OneToOneField(
        Targetingcriteria,
        on_delete=models.DO_NOTHING,
        related_name="targetpopulation_targeting_criteria",
        blank=True,
        null=True,
    )
    program = models.ForeignKey(
        Program, on_delete=models.DO_NOTHING, related_name="targetpopulation_program", blank=True, null=True
    )
    change_date = models.DateTimeField(blank=True, null=True)
    finalized_at = models.DateTimeField(blank=True, null=True)
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="targetpopulation_business_area", blank=True, null=True
    )
    sent_to_datahub = models.BooleanField(null=True)
    ca_hash_id = models.TextField(blank=True, null=True)  # This field type is a guess.
    ca_id = models.TextField(blank=True, null=True)  # This field type is a guess.
    vulnerability_score_max = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    vulnerability_score_min = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    version = models.BigIntegerField(null=True)
    excluded_ids = models.TextField(null=True)
    exclusion_reason = models.TextField(null=True)
    steficon_applied_date = models.DateTimeField(blank=True, null=True)
    adult_female_count = models.IntegerField(blank=True, null=True)
    adult_male_count = models.IntegerField(blank=True, null=True)
    build_status = models.CharField(max_length=256, null=True)
    built_at = models.DateTimeField(blank=True, null=True)
    child_female_count = models.IntegerField(blank=True, null=True)
    child_male_count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "targeting_targetpopulation"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)
