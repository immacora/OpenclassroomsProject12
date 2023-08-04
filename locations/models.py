import uuid
from django.db import models

from helpers.validators import unicodealphavalidator, unicodecharfieldvalidator


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
    zip_code = models.PositiveSmallIntegerField("Code postal")
    country = models.CharField(
        "Nom du pays", max_length=100, validators=[unicodealphavalidator]
    )

    class Meta:
        unique_together = ("street_number", "street_name", "city")

    def __str__(self):
        return f"Adresse : {self.street_number} {self.street_name}, {self.zip_code} {self.city} {self.country}."
