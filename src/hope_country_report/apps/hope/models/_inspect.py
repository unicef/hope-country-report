# flake8: noqa F405.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
# DO NOT rename the models, AND don't rename db_table values or field names.
import django.contrib.postgres.fields
from django.contrib.gis.db import models

from hope_country_report.apps.core.storage import get_hope_storage
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
    kobo_token = models.CharField(max_length=255, blank=True, null=True)
    kobo_url = models.CharField(max_length=255, blank=True, null=True)
    rapid_pro_host = models.CharField(max_length=200, blank=True, null=True)
    rapid_pro_payment_verification_token = models.CharField(max_length=40, blank=True, null=True)
    rapid_pro_messages_token = models.CharField(max_length=40, blank=True, null=True)
    rapid_pro_survey_token = models.CharField(max_length=40, blank=True, null=True)
    slug = models.CharField(unique=True, max_length=250, null=True)
    custom_fields = models.JSONField(null=True)
    has_data_sharing_agreement = models.BooleanField(null=True)
    is_split = models.BooleanField(null=True)
    postpone_deduplication = models.BooleanField(null=True)
    deduplication_duplicate_score = models.FloatField(null=True)
    deduplication_possible_duplicate_score = models.FloatField(null=True)
    deduplication_batch_duplicates_percentage = models.IntegerField(null=True)
    deduplication_batch_duplicates_allowed = models.IntegerField(null=True)
    deduplication_golden_record_duplicates_percentage = models.IntegerField(null=True)
    deduplication_golden_record_duplicates_allowed = models.IntegerField(null=True)
    screen_beneficiary = models.BooleanField(null=True)
    deduplication_ignore_withdraw = models.BooleanField(null=True)
    biometric_deduplication_threshold = models.FloatField(null=True)
    is_accountability_applicable = models.BooleanField(null=True)
    active = models.BooleanField(null=True)
    enable_email_notification = models.BooleanField(null=True)
    parent = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="businessarea_parent", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "core_businessarea"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)


class BusinessareaCountries(HopeModel):
    id = models.BigAutoField(primary_key=True)
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


class Businessareapartnerthrough(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="businessareapartnerthrough_business_area", null=True
    )

    class Meta:
        managed = False
        db_table = "core_businessareapartnerthrough"

    class Tenant:
        tenant_filter_field: str = "__all__"


class BusinessareapartnerthroughRoles(HopeModel):
    id = models.BigAutoField(primary_key=True)
    businessareapartnerthrough = models.ForeignKey(
        Businessareapartnerthrough,
        on_delete=models.DO_NOTHING,
        related_name="businessareapartnerthroughroles_businessareapartnerthrough",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "core_businessareapartnerthrough_roles"

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
    label = models.CharField(max_length=32, null=True)
    code = models.CharField(max_length=32, null=True)
    type = models.CharField(max_length=32, blank=True, null=True)
    description = models.TextField(null=True)
    active = models.BooleanField(null=True)
    deprecated = models.BooleanField(null=True)
    individual_filters_available = models.BooleanField(null=True)
    household_filters_available = models.BooleanField(null=True)
    recalculate_composition = models.BooleanField(null=True)
    weight = models.SmallIntegerField(null=True)

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


class DatacollectingtypeLimitTo(HopeModel):
    id = models.BigAutoField(primary_key=True)
    datacollectingtype = models.ForeignKey(
        DataCollectingType,
        on_delete=models.DO_NOTHING,
        related_name="datacollectingtypelimitto_datacollectingtype",
        null=True,
    )
    businessarea = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="datacollectingtypelimitto_businessarea", null=True
    )

    class Meta:
        managed = False
        db_table = "core_datacollectingtype_limit_to"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Periodicfielddata(HopeModel):
    id = models.BigAutoField(primary_key=True)
    subtype = models.CharField(max_length=16, null=True)
    number_of_rounds = models.IntegerField(null=True)
    rounds_names = models.TextField(null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "core_periodicfielddata"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Area(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    original_id = models.UUIDField(blank=True, null=True)
    name = models.CharField(max_length=255, null=True)
    p_code = models.CharField(unique=True, max_length=32, blank=True, null=True)
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


class Grievancedocument(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    file = models.CharField(max_length=100, blank=True, null=True)
    file_size = models.IntegerField(blank=True, null=True)
    content_type = models.CharField(max_length=100, null=True)
    grievance_ticket = models.ForeignKey(
        "Grievanceticket",
        on_delete=models.DO_NOTHING,
        related_name="grievancedocument_grievance_ticket",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "grievance_grievancedocument"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)


class Grievanceticket(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    version = models.BigIntegerField(null=True)
    unicef_id = models.CharField(max_length=255, blank=True, null=True)
    user_modified = models.DateTimeField(blank=True, null=True)
    last_notification_sent = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(null=True)
    category = models.IntegerField(null=True)
    issue_type = models.IntegerField(blank=True, null=True)
    description = models.TextField(null=True)
    area = models.CharField(max_length=250, null=True)
    language = models.TextField(null=True)
    consent = models.BooleanField(null=True)
    extras = models.JSONField(null=True)
    ignored = models.BooleanField(null=True)
    household_unicef_id = models.CharField(max_length=250, blank=True, null=True)
    priority = models.IntegerField(null=True)
    urgency = models.IntegerField(null=True)
    comments = models.TextField(blank=True, null=True)
    is_original = models.BooleanField(null=True)
    is_migration_handled = models.BooleanField(null=True)
    migrated_at = models.DateTimeField(blank=True, null=True)
    admin2 = models.ForeignKey(
        Area, on_delete=models.DO_NOTHING, related_name="grievanceticket_admin2", blank=True, null=True
    )
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="grievanceticket_business_area", null=True
    )
    copied_from = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="grievanceticket_copied_from", blank=True, null=True
    )
    registration_data_import = models.ForeignKey(
        "DataRegistrationdataimport",
        on_delete=models.DO_NOTHING,
        related_name="grievanceticket_registration_data_import",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "grievance_grievanceticket"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.description)


class GrievanceticketPrograms(HopeModel):
    id = models.BigAutoField(primary_key=True)
    grievanceticket = models.ForeignKey(
        Grievanceticket, on_delete=models.DO_NOTHING, related_name="grievanceticketprograms_grievanceticket", null=True
    )
    program = models.ForeignKey(
        "Program", on_delete=models.DO_NOTHING, related_name="grievanceticketprograms_program", null=True
    )

    class Meta:
        managed = False
        db_table = "grievance_grievanceticket_programs"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Grievanceticketthrough(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    linked_ticket = models.ForeignKey(
        Grievanceticket, on_delete=models.DO_NOTHING, related_name="grievanceticketthrough_linked_ticket", null=True
    )
    main_ticket = models.ForeignKey(
        Grievanceticket, on_delete=models.DO_NOTHING, related_name="grievanceticketthrough_main_ticket", null=True
    )

    class Meta:
        managed = False
        db_table = "grievance_grievanceticketthrough"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Ticketaddindividualdetails(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    individual_data = models.JSONField(blank=True, null=True)
    approve_status = models.BooleanField(null=True)
    household = models.ForeignKey(
        "Household",
        on_delete=models.DO_NOTHING,
        related_name="ticketaddindividualdetails_household",
        blank=True,
        null=True,
    )
    ticket = models.OneToOneField(
        Grievanceticket, on_delete=models.DO_NOTHING, related_name="ticketaddindividualdetails_ticket", null=True
    )

    class Meta:
        managed = False
        db_table = "grievance_ticketaddindividualdetails"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Ticketcomplaintdetails(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    household = models.ForeignKey(
        "Household", on_delete=models.DO_NOTHING, related_name="ticketcomplaintdetails_household", blank=True, null=True
    )
    individual = models.ForeignKey(
        "Individual",
        on_delete=models.DO_NOTHING,
        related_name="ticketcomplaintdetails_individual",
        blank=True,
        null=True,
    )
    ticket = models.OneToOneField(
        Grievanceticket, on_delete=models.DO_NOTHING, related_name="ticketcomplaintdetails_ticket", null=True
    )
    payment = models.ForeignKey(
        "Payment", on_delete=models.DO_NOTHING, related_name="ticketcomplaintdetails_payment", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "grievance_ticketcomplaintdetails"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Ticketdeletehouseholddetails(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    role_reassign_data = models.JSONField(null=True)
    approve_status = models.BooleanField(null=True)
    household = models.ForeignKey(
        "Household",
        on_delete=models.DO_NOTHING,
        related_name="ticketdeletehouseholddetails_household",
        blank=True,
        null=True,
    )
    reason_household = models.ForeignKey(
        "Household",
        on_delete=models.DO_NOTHING,
        related_name="ticketdeletehouseholddetails_reason_household",
        blank=True,
        null=True,
    )
    ticket = models.OneToOneField(
        Grievanceticket, on_delete=models.DO_NOTHING, related_name="ticketdeletehouseholddetails_ticket", null=True
    )

    class Meta:
        managed = False
        db_table = "grievance_ticketdeletehouseholddetails"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Ticketdeleteindividualdetails(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    role_reassign_data = models.JSONField(null=True)
    approve_status = models.BooleanField(null=True)
    individual = models.ForeignKey(
        "Individual",
        on_delete=models.DO_NOTHING,
        related_name="ticketdeleteindividualdetails_individual",
        blank=True,
        null=True,
    )
    ticket = models.OneToOneField(
        Grievanceticket, on_delete=models.DO_NOTHING, related_name="ticketdeleteindividualdetails_ticket", null=True
    )

    class Meta:
        managed = False
        db_table = "grievance_ticketdeleteindividualdetails"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Tickethouseholddataupdatedetails(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    household_data = models.JSONField(blank=True, null=True)
    household = models.ForeignKey(
        "Household",
        on_delete=models.DO_NOTHING,
        related_name="tickethouseholddataupdatedetails_household",
        blank=True,
        null=True,
    )
    ticket = models.OneToOneField(
        Grievanceticket, on_delete=models.DO_NOTHING, related_name="tickethouseholddataupdatedetails_ticket", null=True
    )

    class Meta:
        managed = False
        db_table = "grievance_tickethouseholddataupdatedetails"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Ticketindividualdataupdatedetails(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    individual_data = models.JSONField(blank=True, null=True)
    role_reassign_data = models.JSONField(null=True)
    individual = models.ForeignKey(
        "Individual",
        on_delete=models.DO_NOTHING,
        related_name="ticketindividualdataupdatedetails_individual",
        blank=True,
        null=True,
    )
    ticket = models.OneToOneField(
        Grievanceticket, on_delete=models.DO_NOTHING, related_name="ticketindividualdataupdatedetails_ticket", null=True
    )

    class Meta:
        managed = False
        db_table = "grievance_ticketindividualdataupdatedetails"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Ticketneedsadjudicationdetails(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    is_multiple_duplicates_version = models.BooleanField(null=True)
    role_reassign_data = models.JSONField(null=True)
    extra_data = models.JSONField(null=True)
    score_min = models.FloatField(null=True)
    score_max = models.FloatField(null=True)
    is_cross_area = models.BooleanField(null=True)
    golden_records_individual = models.ForeignKey(
        "Individual",
        on_delete=models.DO_NOTHING,
        related_name="ticketneedsadjudicationdetails_golden_records_individual",
        null=True,
    )
    possible_duplicate = models.ForeignKey(
        "Individual",
        on_delete=models.DO_NOTHING,
        related_name="ticketneedsadjudicationdetails_possible_duplicate",
        blank=True,
        null=True,
    )
    selected_individual = models.ForeignKey(
        "Individual",
        on_delete=models.DO_NOTHING,
        related_name="ticketneedsadjudicationdetails_selected_individual",
        blank=True,
        null=True,
    )
    ticket = models.OneToOneField(
        Grievanceticket, on_delete=models.DO_NOTHING, related_name="ticketneedsadjudicationdetails_ticket", null=True
    )

    class Meta:
        managed = False
        db_table = "grievance_ticketneedsadjudicationdetails"

    class Tenant:
        tenant_filter_field: str = "__all__"


class TicketneedsadjudicationdetailsPossibleDuplicates(HopeModel):
    id = models.BigAutoField(primary_key=True)
    ticketneedsadjudicationdetails = models.ForeignKey(
        Ticketneedsadjudicationdetails,
        on_delete=models.DO_NOTHING,
        related_name="ticketneedsadjudicationdetailspossibleduplicates_ticketneedsadjudicationdetails",
        null=True,
    )
    individual = models.ForeignKey(
        "Individual",
        on_delete=models.DO_NOTHING,
        related_name="ticketneedsadjudicationdetailspossibleduplicates_individual",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "grievance_ticketneedsadjudicationdetails_possible_duplicates"

    class Tenant:
        tenant_filter_field: str = "__all__"


class TicketneedsadjudicationdetailsSelectedDistinct(HopeModel):
    id = models.BigAutoField(primary_key=True)
    ticketneedsadjudicationdetails = models.ForeignKey(
        Ticketneedsadjudicationdetails,
        on_delete=models.DO_NOTHING,
        related_name="ticketneedsadjudicationdetailsselecteddistinct_ticketneedsadjudicationdetails",
        null=True,
    )
    individual = models.ForeignKey(
        "Individual",
        on_delete=models.DO_NOTHING,
        related_name="ticketneedsadjudicationdetailsselecteddistinct_individual",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "grievance_ticketneedsadjudicationdetails_selected_distinct"

    class Tenant:
        tenant_filter_field: str = "__all__"


class TicketneedsadjudicationdetailsSelectedIndividuals(HopeModel):
    id = models.BigAutoField(primary_key=True)
    ticketneedsadjudicationdetails = models.ForeignKey(
        Ticketneedsadjudicationdetails,
        on_delete=models.DO_NOTHING,
        related_name="ticketneedsadjudicationdetailsselectedindividuals_ticketneedsadjudicationdetails",
        null=True,
    )
    individual = models.ForeignKey(
        "Individual",
        on_delete=models.DO_NOTHING,
        related_name="ticketneedsadjudicationdetailsselectedindividuals_individual",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "grievance_ticketneedsadjudicationdetails_selected_individuals"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Ticketnegativefeedbackdetails(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    household = models.ForeignKey(
        "Household",
        on_delete=models.DO_NOTHING,
        related_name="ticketnegativefeedbackdetails_household",
        blank=True,
        null=True,
    )
    individual = models.ForeignKey(
        "Individual",
        on_delete=models.DO_NOTHING,
        related_name="ticketnegativefeedbackdetails_individual",
        blank=True,
        null=True,
    )
    ticket = models.OneToOneField(
        Grievanceticket, on_delete=models.DO_NOTHING, related_name="ticketnegativefeedbackdetails_ticket", null=True
    )

    class Meta:
        managed = False
        db_table = "grievance_ticketnegativefeedbackdetails"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Ticketnote(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    description = models.TextField(null=True)
    ticket = models.ForeignKey(
        Grievanceticket, on_delete=models.DO_NOTHING, related_name="ticketnote_ticket", null=True
    )

    class Meta:
        managed = False
        db_table = "grievance_ticketnote"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.description)


class Ticketpaymentverificationdetails(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    payment_verification_status = models.CharField(max_length=50, null=True)
    new_status = models.CharField(max_length=50, blank=True, null=True)
    old_received_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    new_received_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    approve_status = models.BooleanField(null=True)
    payment_verification = models.ForeignKey(
        "Paymentverification",
        on_delete=models.DO_NOTHING,
        related_name="ticketpaymentverificationdetails_payment_verification",
        blank=True,
        null=True,
    )
    ticket = models.OneToOneField(
        Grievanceticket, on_delete=models.DO_NOTHING, related_name="ticketpaymentverificationdetails_ticket", null=True
    )

    class Meta:
        managed = False
        db_table = "grievance_ticketpaymentverificationdetails"

    class Tenant:
        tenant_filter_field: str = "__all__"


class TicketpaymentverificationdetailsPaymentVerificaf7C9(HopeModel):
    id = models.BigAutoField(primary_key=True)
    ticketpaymentverificationdetails = models.ForeignKey(
        Ticketpaymentverificationdetails,
        on_delete=models.DO_NOTHING,
        related_name="ticketpaymentverificationdetailspaymentverificaf7c9_ticketpaymentverificationdetails",
        null=True,
    )
    paymentverification = models.ForeignKey(
        "Paymentverification",
        on_delete=models.DO_NOTHING,
        related_name="ticketpaymentverificationdetailspaymentverificaf7c9_paymentverification",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "grievance_ticketpaymentverificationdetails_payment_verificaf7c9"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Ticketpositivefeedbackdetails(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    household = models.ForeignKey(
        "Household",
        on_delete=models.DO_NOTHING,
        related_name="ticketpositivefeedbackdetails_household",
        blank=True,
        null=True,
    )
    individual = models.ForeignKey(
        "Individual",
        on_delete=models.DO_NOTHING,
        related_name="ticketpositivefeedbackdetails_individual",
        blank=True,
        null=True,
    )
    ticket = models.OneToOneField(
        Grievanceticket, on_delete=models.DO_NOTHING, related_name="ticketpositivefeedbackdetails_ticket", null=True
    )

    class Meta:
        managed = False
        db_table = "grievance_ticketpositivefeedbackdetails"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Ticketreferraldetails(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    household = models.ForeignKey(
        "Household", on_delete=models.DO_NOTHING, related_name="ticketreferraldetails_household", blank=True, null=True
    )
    individual = models.ForeignKey(
        "Individual",
        on_delete=models.DO_NOTHING,
        related_name="ticketreferraldetails_individual",
        blank=True,
        null=True,
    )
    ticket = models.OneToOneField(
        Grievanceticket, on_delete=models.DO_NOTHING, related_name="ticketreferraldetails_ticket", null=True
    )

    class Meta:
        managed = False
        db_table = "grievance_ticketreferraldetails"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Ticketsensitivedetails(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    household = models.ForeignKey(
        "Household", on_delete=models.DO_NOTHING, related_name="ticketsensitivedetails_household", blank=True, null=True
    )
    individual = models.ForeignKey(
        "Individual",
        on_delete=models.DO_NOTHING,
        related_name="ticketsensitivedetails_individual",
        blank=True,
        null=True,
    )
    ticket = models.OneToOneField(
        Grievanceticket, on_delete=models.DO_NOTHING, related_name="ticketsensitivedetails_ticket", null=True
    )
    payment = models.ForeignKey(
        "Payment", on_delete=models.DO_NOTHING, related_name="ticketsensitivedetails_payment", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "grievance_ticketsensitivedetails"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Ticketsystemflaggingdetails(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    approve_status = models.BooleanField(null=True)
    role_reassign_data = models.JSONField(null=True)
    golden_records_individual = models.ForeignKey(
        "Individual",
        on_delete=models.DO_NOTHING,
        related_name="ticketsystemflaggingdetails_golden_records_individual",
        null=True,
    )
    ticket = models.OneToOneField(
        Grievanceticket, on_delete=models.DO_NOTHING, related_name="ticketsystemflaggingdetails_ticket", null=True
    )

    class Meta:
        managed = False
        db_table = "grievance_ticketsystemflaggingdetails"

    class Tenant:
        tenant_filter_field: str = "__all__"


class BankaccountInfo(HopeModel):
    id = models.UUIDField(primary_key=True)
    rdi_merge_status = models.CharField(max_length=10, null=True)
    is_original = models.BooleanField(null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    is_removed = models.BooleanField(null=True)
    removed_date = models.DateTimeField(blank=True, null=True)
    last_sync_at = models.DateTimeField(blank=True, null=True)
    bank_name = models.CharField(max_length=255, null=True)
    bank_account_number = models.CharField(max_length=64, null=True)
    debit_card_number = models.CharField(max_length=255, null=True)
    bank_branch_name = models.CharField(max_length=255, null=True)
    account_holder_name = models.CharField(max_length=255, null=True)
    copied_from = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="bankaccountinfo_copied_from", blank=True, null=True
    )
    individual = models.ForeignKey(
        "Individual", on_delete=models.DO_NOTHING, related_name="bankaccountinfo_individual", null=True
    )

    class Meta:
        managed = False
        db_table = "household_bankaccountinfo"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Document(HopeModel):
    id = models.UUIDField(primary_key=True)
    rdi_merge_status = models.CharField(max_length=10, null=True)
    is_removed = models.BooleanField(null=True)
    is_original = models.BooleanField(null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    last_sync_at = models.DateTimeField(blank=True, null=True)
    document_number = models.CharField(max_length=255, null=True)
    photo = models.ImageField(storage=get_hope_storage(), null=True)
    status = models.CharField(max_length=20, null=True)
    cleared = models.BooleanField(null=True)
    cleared_date = models.DateTimeField(null=True)
    issuance_date = models.DateTimeField(blank=True, null=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    is_migration_handled = models.BooleanField(null=True)
    copied_from = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="document_copied_from", blank=True, null=True
    )
    country = models.ForeignKey(
        Country, on_delete=models.DO_NOTHING, related_name="document_country", blank=True, null=True
    )
    individual = models.ForeignKey(
        "Individual", on_delete=models.DO_NOTHING, related_name="document_individual", null=True
    )
    program = models.ForeignKey(
        "Program", on_delete=models.DO_NOTHING, related_name="document_program", blank=True, null=True
    )
    type = models.ForeignKey("DocumentType", on_delete=models.DO_NOTHING, related_name="document_type", null=True)

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
    is_original = models.BooleanField(null=True)
    household = models.ForeignKey(
        "Household", on_delete=models.DO_NOTHING, related_name="entitlementcard_household", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "household_entitlementcard"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Household(HopeModel):
    id = models.UUIDField(primary_key=True)
    rdi_merge_status = models.CharField(max_length=10, null=True)
    is_original = models.BooleanField(null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    is_removed = models.BooleanField(null=True)
    removed_date = models.DateTimeField(blank=True, null=True)
    last_sync_at = models.DateTimeField(blank=True, null=True)
    version = models.BigIntegerField(null=True)
    unicef_id = models.CharField(max_length=255, blank=True, null=True)
    withdrawn = models.BooleanField(null=True)
    withdrawn_date = models.DateTimeField(blank=True, null=True)
    consent_sign = models.ImageField(storage=get_hope_storage(), null=True)
    consent = models.BooleanField(blank=True, null=True)
    consent_sharing = models.CharField(max_length=63, null=True)
    residence_status = models.CharField(max_length=254, null=True)
    address = models.TextField(null=True)  # This field type is a guess.
    zip_code = models.CharField(max_length=12, blank=True, null=True)
    geopoint = models.GeometryField(blank=True, null=True)
    size = models.IntegerField(blank=True, null=True)
    female_age_group_0_5_count = models.IntegerField(blank=True, null=True)
    female_age_group_6_11_count = models.IntegerField(blank=True, null=True)
    female_age_group_12_17_count = models.IntegerField(blank=True, null=True)
    female_age_group_18_59_count = models.IntegerField(blank=True, null=True)
    female_age_group_60_count = models.IntegerField(blank=True, null=True)
    pregnant_count = models.IntegerField(blank=True, null=True)
    male_age_group_0_5_count = models.IntegerField(blank=True, null=True)
    male_age_group_6_11_count = models.IntegerField(blank=True, null=True)
    male_age_group_12_17_count = models.IntegerField(blank=True, null=True)
    male_age_group_18_59_count = models.IntegerField(blank=True, null=True)
    male_age_group_60_count = models.IntegerField(blank=True, null=True)
    female_age_group_0_5_disabled_count = models.IntegerField(blank=True, null=True)
    female_age_group_6_11_disabled_count = models.IntegerField(blank=True, null=True)
    female_age_group_12_17_disabled_count = models.IntegerField(blank=True, null=True)
    female_age_group_18_59_disabled_count = models.IntegerField(blank=True, null=True)
    female_age_group_60_disabled_count = models.IntegerField(blank=True, null=True)
    male_age_group_0_5_disabled_count = models.IntegerField(blank=True, null=True)
    male_age_group_6_11_disabled_count = models.IntegerField(blank=True, null=True)
    male_age_group_12_17_disabled_count = models.IntegerField(blank=True, null=True)
    male_age_group_18_59_disabled_count = models.IntegerField(blank=True, null=True)
    male_age_group_60_disabled_count = models.IntegerField(blank=True, null=True)
    children_count = models.IntegerField(blank=True, null=True)
    male_children_count = models.IntegerField(blank=True, null=True)
    female_children_count = models.IntegerField(blank=True, null=True)
    children_disabled_count = models.IntegerField(blank=True, null=True)
    male_children_disabled_count = models.IntegerField(blank=True, null=True)
    female_children_disabled_count = models.IntegerField(blank=True, null=True)
    returnee = models.BooleanField(blank=True, null=True)
    flex_fields = models.JSONField(null=True)
    first_registration_date = models.DateTimeField(null=True)
    last_registration_date = models.DateTimeField(null=True)
    fchild_hoh = models.BooleanField(blank=True, null=True)
    child_hoh = models.BooleanField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    deviceid = models.CharField(max_length=250, null=True)
    name_enumerator = models.CharField(max_length=250, null=True)
    org_enumerator = models.CharField(max_length=250, null=True)
    org_name_enumerator = models.CharField(max_length=250, null=True)
    village = models.CharField(max_length=250, null=True)
    registration_method = models.CharField(max_length=250, null=True)
    collect_individual_data = models.CharField(max_length=250, null=True)
    currency = models.CharField(max_length=250, null=True)
    unhcr_id = models.CharField(max_length=250, null=True)
    internal_data = models.JSONField(null=True)
    detail_id = models.CharField(max_length=150, blank=True, null=True)
    registration_id = models.TextField(blank=True, null=True)  # This field type is a guess.
    program_registration_id = models.TextField(unique=True, blank=True, null=True)  # This field type is a guess.
    total_cash_received_usd = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True)
    total_cash_received = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True)
    family_id = models.CharField(max_length=100, blank=True, null=True)
    origin_unicef_id = models.CharField(max_length=100, blank=True, null=True)
    is_migration_handled = models.BooleanField(null=True)
    migrated_at = models.DateTimeField(blank=True, null=True)
    is_recalculated_group_ages = models.BooleanField(null=True)
    collect_type = models.CharField(max_length=8, null=True)
    kobo_submission_uuid = models.UUIDField(blank=True, null=True)
    kobo_submission_time = models.DateTimeField(blank=True, null=True)
    enumerator_rec_id = models.IntegerField(blank=True, null=True)
    mis_unicef_id = models.CharField(max_length=255, blank=True, null=True)
    flex_registrations_record_id = models.IntegerField(blank=True, null=True)
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
    admin_area = models.ForeignKey(
        Area, on_delete=models.DO_NOTHING, related_name="household_admin_area", blank=True, null=True
    )
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="household_business_area", null=True
    )
    copied_from = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="household_copied_from", blank=True, null=True
    )
    country = models.ForeignKey(
        Country, on_delete=models.DO_NOTHING, related_name="household_country", blank=True, null=True
    )
    country_origin = models.ForeignKey(
        Country, on_delete=models.DO_NOTHING, related_name="household_country_origin", blank=True, null=True
    )
    head_of_household = models.OneToOneField(
        "Individual", on_delete=models.DO_NOTHING, related_name="household_head_of_household", blank=True, null=True
    )
    household_collection = models.ForeignKey(
        "Householdcollection",
        on_delete=models.DO_NOTHING,
        related_name="household_household_collection",
        blank=True,
        null=True,
    )
    program = models.ForeignKey(
        "Program", on_delete=models.DO_NOTHING, related_name="household_program", blank=True, null=True
    )
    registration_data_import = models.ForeignKey(
        "DataRegistrationdataimport",
        on_delete=models.DO_NOTHING,
        related_name="household_registration_data_import",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "household_household"

    class Tenant:
        tenant_filter_field: str = "__all__"


class HouseholdPrograms(HopeModel):
    id = models.BigAutoField(primary_key=True)
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
    rdi_merge_status = models.CharField(max_length=10, null=True)
    is_original = models.BooleanField(null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    is_removed = models.BooleanField(null=True)
    removed_date = models.DateTimeField(blank=True, null=True)
    last_sync_at = models.DateTimeField(blank=True, null=True)
    version = models.BigIntegerField(null=True)
    unicef_id = models.CharField(max_length=255, blank=True, null=True)
    duplicate = models.BooleanField(null=True)
    duplicate_date = models.DateTimeField(blank=True, null=True)
    withdrawn = models.BooleanField(null=True)
    withdrawn_date = models.DateTimeField(blank=True, null=True)
    individual_id = models.CharField(max_length=255, null=True)
    photo = models.ImageField(storage=get_hope_storage(), null=True)
    full_name = models.TextField(null=True)  # This field type is a guess.
    given_name = models.TextField(null=True)  # This field type is a guess.
    middle_name = models.TextField(null=True)  # This field type is a guess.
    family_name = models.TextField(null=True)  # This field type is a guess.
    sex = models.CharField(max_length=255, null=True)
    birth_date = models.DateField(null=True)
    estimated_birth_date = models.BooleanField(null=True)
    marital_status = models.CharField(max_length=255, null=True)
    phone_no = models.CharField(max_length=128, null=True)
    phone_no_valid = models.BooleanField(blank=True, null=True)
    phone_no_alternative = models.CharField(max_length=128, null=True)
    phone_no_alternative_valid = models.BooleanField(blank=True, null=True)
    email = models.CharField(max_length=255, null=True)
    payment_delivery_phone_no = models.CharField(max_length=128, blank=True, null=True)
    relationship = models.CharField(max_length=255, null=True)
    work_status = models.CharField(max_length=20, null=True)
    first_registration_date = models.DateField(null=True)
    last_registration_date = models.DateField(null=True)
    flex_fields = models.JSONField(null=True)
    internal_data = models.JSONField(null=True)
    enrolled_in_nutrition_programme = models.BooleanField(blank=True, null=True)
    administration_of_rutf = models.BooleanField(blank=True, null=True)
    deduplication_golden_record_status = models.CharField(max_length=50, null=True)
    deduplication_batch_status = models.CharField(max_length=50, null=True)
    deduplication_golden_record_results = models.JSONField(null=True)
    deduplication_batch_results = models.JSONField(null=True)
    imported_individual_id = models.UUIDField(blank=True, null=True)
    sanction_list_possible_match = models.BooleanField(null=True)
    sanction_list_confirmed_match = models.BooleanField(null=True)
    pregnant = models.BooleanField(blank=True, null=True)
    disability = models.CharField(max_length=20, null=True)
    observed_disability = models.CharField(max_length=58, null=True)
    disability_certificate_picture = models.ImageField(storage=get_hope_storage(), blank=True, null=True)
    seeing_disability = models.CharField(max_length=50, null=True)
    hearing_disability = models.CharField(max_length=50, null=True)
    physical_disability = models.CharField(max_length=50, null=True)
    memory_disability = models.CharField(max_length=50, null=True)
    selfcare_disability = models.CharField(max_length=50, null=True)
    comms_disability = models.CharField(max_length=50, null=True)
    who_answers_phone = models.CharField(max_length=150, null=True)
    who_answers_alt_phone = models.CharField(max_length=150, null=True)
    fchild_hoh = models.BooleanField(null=True)
    child_hoh = models.BooleanField(null=True)
    detail_id = models.CharField(max_length=150, blank=True, null=True)
    registration_id = models.TextField(blank=True, null=True)  # This field type is a guess.
    program_registration_id = models.TextField(blank=True, null=True)  # This field type is a guess.
    preferred_language = models.CharField(max_length=6, blank=True, null=True)
    relationship_confirmed = models.BooleanField(null=True)
    age_at_registration = models.SmallIntegerField(blank=True, null=True)
    wallet_name = models.CharField(max_length=64, null=True)
    blockchain_name = models.CharField(max_length=64, null=True)
    wallet_address = models.CharField(max_length=128, null=True)
    origin_unicef_id = models.CharField(max_length=100, blank=True, null=True)
    is_migration_handled = models.BooleanField(null=True)
    migrated_at = models.DateTimeField(blank=True, null=True)
    mis_unicef_id = models.CharField(max_length=255, blank=True, null=True)
    vector_column = models.TextField(blank=True, null=True)  # This field type is a guess.
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="individual_business_area", null=True
    )
    copied_from = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="individual_copied_from", blank=True, null=True
    )
    household = models.ForeignKey(
        Household, on_delete=models.DO_NOTHING, related_name="individual_household", blank=True, null=True
    )
    individual_collection = models.ForeignKey(
        "Individualcollection",
        on_delete=models.DO_NOTHING,
        related_name="individual_individual_collection",
        blank=True,
        null=True,
    )
    program = models.ForeignKey(
        "Program", on_delete=models.DO_NOTHING, related_name="individual_program", blank=True, null=True
    )
    registration_data_import = models.ForeignKey(
        "DataRegistrationdataimport",
        on_delete=models.DO_NOTHING,
        related_name="individual_registration_data_import",
        null=True,
    )
    biometric_deduplication_batch_results = models.JSONField(null=True)
    biometric_deduplication_batch_status = models.CharField(max_length=50, null=True)
    biometric_deduplication_golden_record_results = models.JSONField(null=True)
    biometric_deduplication_golden_record_status = models.CharField(max_length=50, null=True)

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
    created = models.DateTimeField(null=True)
    modified = models.DateTimeField(null=True)
    rdi_merge_status = models.CharField(max_length=10, null=True)
    is_removed = models.BooleanField(null=True)
    is_original = models.BooleanField(null=True)
    number = models.CharField(max_length=255, null=True)
    is_migration_handled = models.BooleanField(null=True)
    copied_from = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="individualidentity_copied_from", blank=True, null=True
    )
    country = models.ForeignKey(
        Country, on_delete=models.DO_NOTHING, related_name="individualidentity_country", blank=True, null=True
    )
    individual = models.ForeignKey(
        Individual, on_delete=models.DO_NOTHING, related_name="individualidentity_individual", null=True
    )

    class Meta:
        managed = False
        db_table = "household_individualidentity"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Individualroleinhousehold(HopeModel):
    id = models.UUIDField(primary_key=True)
    rdi_merge_status = models.CharField(max_length=10, null=True)
    is_removed = models.BooleanField(null=True)
    is_original = models.BooleanField(null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    last_sync_at = models.DateTimeField(blank=True, null=True)
    role = models.CharField(max_length=255, null=True)
    is_migration_handled = models.BooleanField(null=True)
    migrated_at = models.DateTimeField(blank=True, null=True)
    copied_from = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="individualroleinhousehold_copied_from", blank=True, null=True
    )
    household = models.ForeignKey(
        Household, on_delete=models.DO_NOTHING, related_name="individualroleinhousehold_household", null=True
    )
    individual = models.ForeignKey(
        Individual, on_delete=models.DO_NOTHING, related_name="individualroleinhousehold_individual", null=True
    )

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
    approval_number_required = models.IntegerField(null=True)
    authorization_number_required = models.IntegerField(null=True)
    finance_release_number_required = models.IntegerField(null=True)
    payment_plan = models.ForeignKey(
        "PaymentPlan", on_delete=models.DO_NOTHING, related_name="approvalprocess_payment_plan", null=True
    )

    class Meta:
        managed = False
        db_table = "payment_approvalprocess"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Deliverymechanism(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    payment_gateway_id = models.CharField(unique=True, max_length=255, blank=True, null=True)
    code = models.CharField(unique=True, max_length=255, null=True)
    name = models.CharField(unique=True, max_length=255, null=True)
    optional_fields = models.TextField(null=True)  # This field type is a guess.
    required_fields = models.TextField(null=True)  # This field type is a guess.
    unique_fields = models.TextField(null=True)  # This field type is a guess.
    is_active = models.BooleanField(null=True)
    transfer_type = models.CharField(max_length=255, null=True)

    class Meta:
        managed = False
        db_table = "payment_deliverymechanism"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)


class Deliverymechanismdata(HopeModel):
    id = models.UUIDField(primary_key=True)
    rdi_merge_status = models.CharField(max_length=10, null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    signature_hash = models.CharField(max_length=40, null=True)
    data = models.JSONField(null=True)
    is_valid = models.BooleanField(null=True)
    validation_errors = models.JSONField(null=True)
    unique_key = models.CharField(unique=True, max_length=256, blank=True, null=True)
    delivery_mechanism = models.ForeignKey(
        Deliverymechanism,
        on_delete=models.DO_NOTHING,
        related_name="deliverymechanismdata_delivery_mechanism",
        null=True,
    )
    individual = models.ForeignKey(
        Individual, on_delete=models.DO_NOTHING, related_name="deliverymechanismdata_individual", null=True
    )
    possible_duplicate_of = models.ForeignKey(
        "self",
        on_delete=models.DO_NOTHING,
        related_name="deliverymechanismdata_possible_duplicate_of",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "payment_deliverymechanismdata"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Deliverymechanismperpaymentplan(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    sent_date = models.DateTimeField(null=True)
    status = models.CharField(max_length=50, null=True)
    delivery_mechanism_order = models.IntegerField(null=True)
    sent_to_payment_gateway = models.BooleanField(null=True)
    chosen_configuration = models.CharField(max_length=50, blank=True, null=True)
    delivery_mechanism = models.ForeignKey(
        Deliverymechanism,
        on_delete=models.DO_NOTHING,
        related_name="deliverymechanismperpaymentplan_delivery_mechanism",
        blank=True,
        null=True,
    )
    financial_service_provider = models.ForeignKey(
        "Financialserviceprovider",
        on_delete=models.DO_NOTHING,
        related_name="deliverymechanismperpaymentplan_financial_service_provider",
        blank=True,
        null=True,
    )
    payment_plan = models.ForeignKey(
        "PaymentPlan",
        on_delete=models.DO_NOTHING,
        related_name="deliverymechanismperpaymentplan_payment_plan",
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
    distribution_limit = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    communication_channel = models.CharField(max_length=6, null=True)
    data_transfer_configuration = models.JSONField(blank=True, null=True)
    payment_gateway_id = models.CharField(max_length=255, blank=True, null=True)
    internal_data = models.JSONField(null=True)

    class Meta:
        managed = False
        db_table = "payment_financialserviceprovider"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)


class FinancialserviceproviderAllowedBusinessAreas(HopeModel):
    id = models.BigAutoField(primary_key=True)
    financialserviceprovider = models.ForeignKey(
        Financialserviceprovider,
        on_delete=models.DO_NOTHING,
        related_name="financialserviceproviderallowedbusinessareas_financialserviceprovider",
        null=True,
    )
    businessarea = models.ForeignKey(
        BusinessArea,
        on_delete=models.DO_NOTHING,
        related_name="financialserviceproviderallowedbusinessareas_businessarea",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "payment_financialserviceprovider_allowed_business_areas"

    class Tenant:
        tenant_filter_field: str = "__all__"


class FinancialserviceproviderDeliveryMechanisms(HopeModel):
    id = models.BigAutoField(primary_key=True)
    financialserviceprovider = models.ForeignKey(
        Financialserviceprovider,
        on_delete=models.DO_NOTHING,
        related_name="financialserviceproviderdeliverymechanisms_financialserviceprovider",
        null=True,
    )
    deliverymechanism = models.ForeignKey(
        Deliverymechanism,
        on_delete=models.DO_NOTHING,
        related_name="financialserviceproviderdeliverymechanisms_deliverymechanism",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "payment_financialserviceprovider_delivery_mechanisms"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Financialserviceproviderxlsxtemplate(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    name = models.CharField(max_length=120, null=True)
    columns = models.CharField(max_length=1000, null=True)
    core_fields = models.TextField(null=True)  # This field type is a guess.
    flex_fields = models.TextField(null=True)  # This field type is a guess.
    document_types = models.TextField(null=True)  # This field type is a guess.

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
    delivery_mechanism = models.ForeignKey(
        Deliverymechanism,
        on_delete=models.DO_NOTHING,
        related_name="fspxlsxtemplateperdeliverymechanism_delivery_mechanism",
        blank=True,
        null=True,
    )
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
    unicef_id = models.CharField(max_length=255, blank=True, null=True)
    signature_hash = models.CharField(max_length=40, null=True)
    status = models.CharField(max_length=255, null=True)
    status_date = models.DateTimeField(null=True)
    currency = models.CharField(max_length=4, blank=True, null=True)
    entitlement_quantity = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    entitlement_quantity_usd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    delivered_quantity = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    delivered_quantity_usd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    delivery_date = models.DateTimeField(blank=True, null=True)
    transaction_reference_id = models.CharField(max_length=255, blank=True, null=True)
    transaction_status_blockchain_link = models.CharField(max_length=255, blank=True, null=True)
    conflicted = models.BooleanField(null=True)
    excluded = models.BooleanField(null=True)
    entitlement_date = models.DateTimeField(blank=True, null=True)
    is_follow_up = models.BooleanField(null=True)
    reason_for_unsuccessful_payment = models.CharField(max_length=255, blank=True, null=True)
    order_number = models.IntegerField(blank=True, null=True)
    token_number = models.IntegerField(blank=True, null=True)
    additional_collector_name = models.CharField(max_length=64, blank=True, null=True)
    additional_document_type = models.CharField(max_length=128, blank=True, null=True)
    additional_document_number = models.CharField(max_length=128, blank=True, null=True)
    fsp_auth_code = models.CharField(max_length=128, blank=True, null=True)
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="payment_business_area", null=True
    )
    collector = models.ForeignKey(Individual, on_delete=models.DO_NOTHING, related_name="payment_collector", null=True)
    delivery_type = models.ForeignKey(
        Deliverymechanism, on_delete=models.DO_NOTHING, related_name="payment_delivery_type", blank=True, null=True
    )
    financial_service_provider = models.ForeignKey(
        Financialserviceprovider,
        on_delete=models.DO_NOTHING,
        related_name="payment_financial_service_provider",
        blank=True,
        null=True,
    )
    head_of_household = models.ForeignKey(
        Individual, on_delete=models.DO_NOTHING, related_name="payment_head_of_household", blank=True, null=True
    )
    household = models.ForeignKey(Household, on_delete=models.DO_NOTHING, related_name="payment_household", null=True)
    parent = models.ForeignKey("PaymentPlan", on_delete=models.DO_NOTHING, related_name="payment_parent", null=True)
    program = models.ForeignKey(
        "Program", on_delete=models.DO_NOTHING, related_name="payment_program", blank=True, null=True
    )
    source_payment = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="payment_source_payment", blank=True, null=True
    )
    is_cash_assist = models.BooleanField(null=True)
    internal_data = models.JSONField(null=True)
    vulnerability_score = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)

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
    version = models.BigIntegerField(null=True)
    unicef_id = models.CharField(max_length=255, blank=True, null=True)
    status_date = models.DateTimeField(null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
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
    background_action_status = models.CharField(max_length=50, blank=True, null=True)
    currency = models.CharField(max_length=4, blank=True, null=True)
    dispersion_start_date = models.DateField(blank=True, null=True)
    dispersion_end_date = models.DateField(blank=True, null=True)
    female_children_count = models.IntegerField(null=True)
    male_children_count = models.IntegerField(null=True)
    female_adults_count = models.IntegerField(null=True)
    male_adults_count = models.IntegerField(null=True)
    total_households_count = models.IntegerField(null=True)
    total_individuals_count = models.IntegerField(null=True)
    imported_file_date = models.DateTimeField(blank=True, null=True)
    steficon_applied_date = models.DateTimeField(blank=True, null=True)
    is_follow_up = models.BooleanField(null=True)
    exclusion_reason = models.TextField(null=True)
    exclude_household_error = models.TextField(null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="paymentplan_business_area", null=True
    )
    program_cycle = models.ForeignKey(
        "ProgramCycle", on_delete=models.DO_NOTHING, related_name="paymentplan_program_cycle", null=True
    )
    source_payment_plan = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, related_name="paymentplan_source_payment_plan", blank=True, null=True
    )
    target_population = models.ForeignKey(
        "TargetPopulation",
        on_delete=models.DO_NOTHING,
        related_name="paymentplan_target_population",
        blank=True,
        null=True,
    )
    internal_data = models.JSONField(null=True)
    is_cash_assist = models.BooleanField(null=True)
    build_status = models.CharField(max_length=50, blank=True, null=True)
    built_at = models.DateTimeField(blank=True, null=True)
    excluded_ids = models.TextField(null=True)
    steficon_targeting_applied_date = models.DateTimeField(blank=True, null=True)
    targeting_criteria = models.OneToOneField(
        "Targetingcriteria",
        on_delete=models.DO_NOTHING,
        related_name="paymentplan_targeting_criteria",
        blank=True,
        null=True,
    )
    vulnerability_score_max = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    vulnerability_score_min = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "payment_paymentplan"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)


class Paymentplansplit(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    split_type = models.CharField(max_length=24, null=True)
    chunks_no = models.IntegerField(blank=True, null=True)
    sent_to_payment_gateway = models.BooleanField(null=True)
    order = models.IntegerField(null=True)
    payment_plan = models.ForeignKey(
        PaymentPlan, on_delete=models.DO_NOTHING, related_name="paymentplansplit_payment_plan", null=True
    )

    class Meta:
        managed = False
        db_table = "payment_paymentplansplit"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Paymentplansplitpayments(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    payment = models.ForeignKey(
        Payment, on_delete=models.DO_NOTHING, related_name="paymentplansplitpayments_payment", null=True
    )
    payment_plan_split = models.ForeignKey(
        Paymentplansplit,
        on_delete=models.DO_NOTHING,
        related_name="paymentplansplitpayments_payment_plan_split",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "payment_paymentplansplitpayments"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Paymentplansupportingdocument(HopeModel):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255, null=True)
    file = models.CharField(max_length=100, null=True)
    uploaded_at = models.DateTimeField(null=True)
    payment_plan = models.ForeignKey(
        PaymentPlan, on_delete=models.DO_NOTHING, related_name="paymentplansupportingdocument_payment_plan", null=True
    )

    class Meta:
        managed = False
        db_table = "payment_paymentplansupportingdocument"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Paymentverification(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    version = models.BigIntegerField(null=True)
    status = models.CharField(max_length=50, null=True)
    status_date = models.DateTimeField(blank=True, null=True)
    received_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    sent_to_rapid_pro = models.BooleanField(null=True)
    payment_verification_plan = models.ForeignKey(
        "Paymentverificationplan",
        on_delete=models.DO_NOTHING,
        related_name="paymentverification_payment_verification_plan",
        null=True,
    )
    payment = models.ForeignKey(
        Payment, on_delete=models.DO_NOTHING, related_name="paymentverification_payment", null=True
    )

    class Meta:
        managed = False
        db_table = "payment_paymentverification"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Paymentverificationplan(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    version = models.BigIntegerField(null=True)
    unicef_id = models.CharField(max_length=255, blank=True, null=True)
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
    rapid_pro_flow_start_uuids = models.TextField(null=True)  # This field type is a guess.
    age_filter = models.JSONField(blank=True, null=True)
    excluded_admin_areas_filter = models.JSONField(blank=True, null=True)
    sex_filter = models.CharField(max_length=10, blank=True, null=True)
    activation_date = models.DateTimeField(blank=True, null=True)
    completion_date = models.DateTimeField(blank=True, null=True)
    xlsx_file_exporting = models.BooleanField(null=True)
    xlsx_file_imported = models.BooleanField(null=True)
    error = models.CharField(max_length=500, blank=True, null=True)
    payment_plan = models.ForeignKey(
        PaymentPlan,
        on_delete=models.DO_NOTHING,
        related_name="paymentverificationplan_payment_plan",
        blank=True,
        null=True,
    )

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
    payment_plan = models.OneToOneField(
        PaymentPlan,
        on_delete=models.DO_NOTHING,
        related_name="paymentverificationsummary_payment_plan",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "payment_paymentverificationsummary"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Beneficiarygroup(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    name = models.CharField(unique=True, max_length=255, null=True)
    group_label = models.CharField(max_length=255, null=True)
    group_label_plural = models.CharField(max_length=255, null=True)
    member_label = models.CharField(max_length=255, null=True)
    member_label_plural = models.CharField(max_length=255, null=True)
    master_detail = models.BooleanField(null=True)

    class Meta:
        managed = False
        db_table = "program_beneficiarygroup"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)


class Program(HopeModel):
    is_removed = models.BooleanField(null=True)
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    last_sync_at = models.DateTimeField(blank=True, null=True)
    version = models.BigIntegerField(null=True)
    name = models.TextField(null=True)  # This field type is a guess.
    status = models.CharField(max_length=10, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=255, null=True)
    ca_id = models.TextField(blank=True, null=True)  # This field type is a guess.
    ca_hash_id = models.TextField(blank=True, null=True)  # This field type is a guess.
    budget = models.DecimalField(max_digits=11, decimal_places=2, null=True)
    frequency_of_payments = models.CharField(max_length=50, null=True)
    sector = models.CharField(max_length=50, null=True)
    scope = models.CharField(max_length=50, blank=True, null=True)
    cash_plus = models.BooleanField(null=True)
    population_goal = models.IntegerField(null=True)
    administrative_areas_of_implementation = models.CharField(max_length=255, null=True)
    is_visible = models.BooleanField(null=True)
    household_count = models.IntegerField(null=True)
    individual_count = models.IntegerField(null=True)
    programme_code = models.CharField(max_length=4, blank=True, null=True)
    partner_access = models.CharField(max_length=50, null=True)
    biometric_deduplication_enabled = models.BooleanField(null=True)
    deduplication_set_id = models.UUIDField(blank=True, null=True)
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="program_business_area", null=True
    )
    data_collecting_type = models.ForeignKey(
        DataCollectingType, on_delete=models.DO_NOTHING, related_name="program_data_collecting_type", null=True
    )
    beneficiary_group = models.ForeignKey(
        Beneficiarygroup, on_delete=models.DO_NOTHING, related_name="program_beneficiary_group", null=True
    )

    class Meta:
        managed = False
        db_table = "program_program"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)


class ProgramAdminAreas(HopeModel):
    id = models.BigAutoField(primary_key=True)
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
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    version = models.BigIntegerField(null=True)
    unicef_id = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(blank=True, null=True)
    program = models.ForeignKey(Program, on_delete=models.DO_NOTHING, related_name="programcycle_program", null=True)

    class Meta:
        managed = False
        db_table = "program_programcycle"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Programpartnerthrough(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    full_area_access = models.BooleanField(null=True)
    program = models.ForeignKey(
        Program, on_delete=models.DO_NOTHING, related_name="programpartnerthrough_program", null=True
    )

    class Meta:
        managed = False
        db_table = "program_programpartnerthrough"

    class Tenant:
        tenant_filter_field: str = "__all__"


class ProgrampartnerthroughAreas(HopeModel):
    id = models.BigAutoField(primary_key=True)
    programpartnerthrough = models.ForeignKey(
        Programpartnerthrough,
        on_delete=models.DO_NOTHING,
        related_name="programpartnerthroughareas_programpartnerthrough",
        null=True,
    )
    area = models.ForeignKey(
        Area, on_delete=models.DO_NOTHING, related_name="programpartnerthroughareas_area", null=True
    )

    class Meta:
        managed = False
        db_table = "program_programpartnerthrough_areas"

    class Tenant:
        tenant_filter_field: str = "__all__"


class DataDeduplicationenginesimilaritypair(HopeModel):
    id = models.BigAutoField(primary_key=True)
    similarity_score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    individual1 = models.ForeignKey(
        Individual,
        on_delete=models.DO_NOTHING,
        related_name="datadeduplicationenginesimilaritypair_individual1",
        null=True,
    )
    individual2 = models.ForeignKey(
        Individual,
        on_delete=models.DO_NOTHING,
        related_name="datadeduplicationenginesimilaritypair_individual2",
        null=True,
    )
    program = models.ForeignKey(
        Program, on_delete=models.DO_NOTHING, related_name="datadeduplicationenginesimilaritypair_program", null=True
    )

    class Meta:
        managed = False
        db_table = "registration_data_deduplicationenginesimilaritypair"

    class Tenant:
        tenant_filter_field: str = "__all__"


class DataImportdata(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=40, null=True)
    business_area_slug = models.CharField(max_length=200, null=True)
    file = models.CharField(max_length=100, blank=True, null=True)
    data_type = models.CharField(max_length=4, null=True)
    number_of_households = models.IntegerField(blank=True, null=True)
    number_of_individuals = models.IntegerField(blank=True, null=True)
    error = models.TextField(null=True)
    validation_errors = models.TextField(null=True)
    delivery_mechanisms_validation_errors = models.TextField(null=True)
    created_by_id = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "registration_data_importdata"

    class Tenant:
        tenant_filter_field: str = "__all__"


class DataKoboimportdata(HopeModel):
    importdata_ptr = models.OneToOneField(
        DataImportdata, on_delete=models.DO_NOTHING, related_name="datakoboimportdata_importdata_ptr", null=True
    )
    kobo_asset_id = models.CharField(max_length=100, null=True)
    only_active_submissions = models.BooleanField(null=True)
    pull_pictures = models.BooleanField(null=True)

    class Meta:
        managed = False
        db_table = "registration_data_koboimportdata"

    class Tenant:
        tenant_filter_field: str = "__all__"


class DataKoboimportedsubmission(HopeModel):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(blank=True, null=True)
    kobo_submission_uuid = models.UUIDField(null=True)
    kobo_asset_id = models.CharField(max_length=150, null=True)
    kobo_submission_time = models.DateTimeField(null=True)
    amended = models.BooleanField(null=True)
    imported_household = models.ForeignKey(
        Household,
        on_delete=models.DO_NOTHING,
        related_name="datakoboimportedsubmission_imported_household",
        blank=True,
        null=True,
    )
    registration_data_import = models.ForeignKey(
        "DataRegistrationdataimport",
        on_delete=models.DO_NOTHING,
        related_name="datakoboimportedsubmission_registration_data_import",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "registration_data_koboimportedsubmission"

    class Tenant:
        tenant_filter_field: str = "__all__"


class DataRegistrationdataimport(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    version = models.BigIntegerField(null=True)
    name = models.TextField(unique=True, null=True)  # This field type is a guess.
    status = models.CharField(max_length=255, null=True)
    import_date = models.DateTimeField(null=True)
    data_source = models.CharField(max_length=255, null=True)
    number_of_individuals = models.IntegerField(null=True)
    number_of_households = models.IntegerField(null=True)
    batch_duplicates = models.IntegerField(null=True)
    batch_possible_duplicates = models.IntegerField(null=True)
    batch_unique = models.IntegerField(null=True)
    golden_record_duplicates = models.IntegerField(null=True)
    golden_record_possible_duplicates = models.IntegerField(null=True)
    golden_record_unique = models.IntegerField(null=True)
    dedup_engine_batch_duplicates = models.IntegerField(null=True)
    dedup_engine_golden_record_duplicates = models.IntegerField(null=True)
    datahub_id = models.UUIDField(blank=True, null=True)
    error_message = models.TextField(null=True)
    sentry_id = models.CharField(max_length=100, blank=True, null=True)
    pull_pictures = models.BooleanField(null=True)
    screen_beneficiary = models.BooleanField(null=True)
    excluded = models.BooleanField(null=True)
    erased = models.BooleanField(null=True)
    refuse_reason = models.CharField(max_length=100, blank=True, null=True)
    allow_delivery_mechanisms_validation_errors = models.BooleanField(null=True)
    deduplication_engine_status = models.CharField(max_length=255, blank=True, null=True)
    business_area = models.ForeignKey(
        BusinessArea,
        on_delete=models.DO_NOTHING,
        related_name="dataregistrationdataimport_business_area",
        blank=True,
        null=True,
    )
    import_data = models.OneToOneField(
        DataImportdata,
        on_delete=models.DO_NOTHING,
        related_name="dataregistrationdataimport_import_data",
        blank=True,
        null=True,
    )
    program = models.ForeignKey(
        Program, on_delete=models.DO_NOTHING, related_name="dataregistrationdataimport_program", blank=True, null=True
    )
    import_from_ids = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "registration_data_registrationdataimport"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)


class DataRegistrationdataimportdatahub(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    name = models.CharField(max_length=255, null=True)
    import_date = models.DateTimeField(null=True)
    hct_id = models.UUIDField(blank=True, null=True)
    import_done = models.CharField(max_length=15, null=True)
    business_area_slug = models.CharField(max_length=250, null=True)
    import_data = models.OneToOneField(
        DataImportdata,
        on_delete=models.DO_NOTHING,
        related_name="dataregistrationdataimportdatahub_import_data",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "registration_data_registrationdataimportdatahub"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)


class Householdselection(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    vulnerability_score = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    is_original = models.BooleanField(null=True)
    is_migration_handled = models.BooleanField(null=True)
    household = models.ForeignKey(
        Household, on_delete=models.DO_NOTHING, related_name="householdselection_household", null=True
    )
    target_population = models.ForeignKey(
        "TargetPopulation", on_delete=models.DO_NOTHING, related_name="householdselection_target_population", null=True
    )

    class Meta:
        managed = False
        db_table = "targeting_householdselection"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Targetingcollectorblockrulefilter(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    field_name = models.CharField(max_length=120, null=True)
    comparison_method = models.CharField(max_length=20, null=True)
    flex_field_classification = models.CharField(max_length=20, null=True)
    arguments = models.JSONField(null=True)
    collector_block_filters = models.ForeignKey(
        "Targetingcollectorrulefilterblock",
        on_delete=models.DO_NOTHING,
        related_name="targetingcollectorblockrulefilter_collector_block_filters",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "targeting_targetingcollectorblockrulefilter"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Targetingcollectorrulefilterblock(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    targeting_criteria_rule = models.ForeignKey(
        "Targetingcriteriarule",
        on_delete=models.DO_NOTHING,
        related_name="targetingcollectorrulefilterblock_targeting_criteria_rule",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "targeting_targetingcollectorrulefilterblock"

    class Tenant:
        tenant_filter_field: str = "__all__"


class Targetingcriteria(HopeModel):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    flag_exclude_if_active_adjudication_ticket = models.BooleanField(null=True)
    flag_exclude_if_on_sanction_list = models.BooleanField(null=True)
    household_ids = models.TextField(null=True)
    individual_ids = models.TextField(null=True)

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
    household_ids = models.TextField(null=True)
    individual_ids = models.TextField(null=True)

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
    flex_field_classification = models.CharField(max_length=20, null=True)
    field_name = models.CharField(max_length=50, null=True)
    arguments = models.JSONField(null=True)
    round_number = models.IntegerField(blank=True, null=True)
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
    flex_field_classification = models.CharField(max_length=20, null=True)
    field_name = models.CharField(max_length=50, null=True)
    arguments = models.JSONField(null=True)
    round_number = models.IntegerField(blank=True, null=True)
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
    target_only_hoh = models.BooleanField(null=True)
    targeting_criteria_rule = models.ForeignKey(
        Targetingcriteriarule,
        on_delete=models.DO_NOTHING,
        related_name="targetingindividualrulefilterblock_targeting_criteria_rule",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "targeting_targetingindividualrulefilterblock"

    class Tenant:
        tenant_filter_field: str = "__all__"


class TargetPopulation(HopeModel):
    is_removed = models.BooleanField(null=True)
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    version = models.BigIntegerField(null=True)
    name = models.TextField(null=True)  # This field type is a guess.
    ca_id = models.TextField(blank=True, null=True)  # This field type is a guess.
    ca_hash_id = models.TextField(blank=True, null=True)  # This field type is a guess.
    change_date = models.DateTimeField(blank=True, null=True)
    finalized_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=256, null=True)
    build_status = models.CharField(max_length=256, null=True)
    built_at = models.DateTimeField(blank=True, null=True)
    sent_to_datahub = models.BooleanField(null=True)
    steficon_applied_date = models.DateTimeField(blank=True, null=True)
    vulnerability_score_min = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    vulnerability_score_max = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    excluded_ids = models.TextField(null=True)
    exclusion_reason = models.TextField(null=True)
    total_households_count = models.IntegerField(blank=True, null=True)
    total_individuals_count = models.IntegerField(blank=True, null=True)
    child_male_count = models.IntegerField(blank=True, null=True)
    child_female_count = models.IntegerField(blank=True, null=True)
    adult_male_count = models.IntegerField(blank=True, null=True)
    adult_female_count = models.IntegerField(blank=True, null=True)
    business_area = models.ForeignKey(
        BusinessArea, on_delete=models.DO_NOTHING, related_name="targetpopulation_business_area", blank=True, null=True
    )
    program = models.ForeignKey(
        Program, on_delete=models.DO_NOTHING, related_name="targetpopulation_program", null=True
    )
    program_cycle = models.ForeignKey(
        ProgramCycle, on_delete=models.DO_NOTHING, related_name="targetpopulation_program_cycle", null=True
    )
    targeting_criteria = models.OneToOneField(
        Targetingcriteria,
        on_delete=models.DO_NOTHING,
        related_name="targetpopulation_targeting_criteria",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "targeting_targetpopulation"

    class Tenant:
        tenant_filter_field: str = "__all__"

    def __str__(self) -> str:
        return str(self.name)
