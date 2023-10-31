from django.db import models
from django.utils.translation import gettext_lazy as _

from .._base import HopeModel


class DocumentType(HopeModel):
    label = models.CharField(max_length=100)
    key = models.CharField(max_length=50, unique=True)
    is_identity_document = models.BooleanField(default=True)
    unique_for_individual = models.BooleanField(default=False)
    valid_for_deduplication = models.BooleanField(default=False)

    class Meta:
        db_table = "core_datacollectingtype"
        ordering = [
            "label",
        ]

    class Tenant:
        tenant_filter_field = "__all__"

    def __str__(self) -> str:
        return f"{self.label}"


class Document(HopeModel):
    STATUS_PENDING = "PENDING"
    STATUS_VALID = "VALID"
    STATUS_NEED_INVESTIGATION = "NEED_INVESTIGATION"
    STATUS_INVALID = "INVALID"
    STATUS_CHOICES = (
        (STATUS_PENDING, _("Pending")),
        (STATUS_VALID, _("Valid")),
        (STATUS_NEED_INVESTIGATION, _("Need Investigation")),
        (STATUS_INVALID, _("Invalid")),
    )

    document_number = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    individual = models.ForeignKey("Individual", related_name="documents", on_delete=models.CASCADE)
    type = models.ForeignKey("DocumentType", related_name="documents", on_delete=models.CASCADE)
    country = models.ForeignKey("hope.Country", blank=True, null=True, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    cleared = models.BooleanField(default=False)
    cleared_date = models.DateTimeField()
    cleared_by = models.ForeignKey("hope.User", null=True, on_delete=models.SET_NULL)
    issuance_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True, db_index=True)
    program = models.ForeignKey("hope.Program", null=True, related_name="+", on_delete=models.CASCADE)

    is_migration_handled = models.BooleanField(default=False)
    copied_from = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="copied_to",
        help_text="If this object was copied from another, this field will contain the object it was copied from.",
    )

    class Meta:
        db_table = "core_datacollectingtype"

    class Tenant:
        tenant_filter_field = "__all__"
