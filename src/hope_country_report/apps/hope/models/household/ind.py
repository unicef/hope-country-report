from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models import JSONField

from .._base import HopeModel


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
