import uuid
from django.db import models

from helpers.validators import (
    unicodealphavalidator,
    unicodecharfieldvalidator,
    digitalcharfieldvalidator,
)


class Location(models.Model):
    """Location of companies and events."""

    location_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    street_number = models.PositiveSmallIntegerField("Numéro de la rue", blank=True)
    street_name = models.CharField(
        "Nom de la rue", max_length=150, validators=[unicodecharfieldvalidator]
    )
    city = models.CharField(
        "Nom de la ville", max_length=100, validators=[unicodealphavalidator]
    )
    zip_code = models.CharField(
        "Code postal", max_length=5, validators=[digitalcharfieldvalidator]
    )
    country = models.CharField(
        "Nom du pays", max_length=100, validators=[unicodealphavalidator]
    )

    class Meta:
        unique_together = ("street_number", "street_name", "city")
        ordering = ["zip_code"]

    def __str__(self):
        return f"{self.street_number} {self.street_name}, {self.zip_code}, {self.city} - {self.country}"
