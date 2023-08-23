import uuid
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from helpers.models import TimestampedModel
from helpers.validators import (
    unicodealphavalidator,
    unicodecharfieldvalidator,
    digitalcharfieldvalidator,
)
from accounts.models import Employee
from locations.models import Location


class Client(TimestampedModel):
    """Epic Events clients with unique SIREN to avoid duplicates."""

    client_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(
        "Nom de l'entreprise", max_length=150, validators=[unicodecharfieldvalidator]
    )
    siren = models.CharField(
        "Numéro SIREN", max_length=9, unique=True, validators=[digitalcharfieldvalidator]
    )
    first_name = models.CharField(
        "Prénom du client",
        max_length=100,
        blank=True,
        validators=[unicodealphavalidator],
    )
    last_name = models.CharField(
        "Nom du client", max_length=100, blank=True, validators=[unicodealphavalidator]
    )
    email = models.EmailField("Email du client", blank=True)
    phone_number = PhoneNumberField(blank=True)
    sales_contact = models.ForeignKey(
        to=Employee,
        on_delete=models.SET_NULL,
        verbose_name="Commercial",
        null=True,
        blank=True,
    )
    locations = models.ManyToManyField(Location, blank=True)

    class Meta:
        ordering = ["company_name"]

    def __str__(self):
        return f"Client {self.last_name} {self.first_name} de la société {self.company_name}"
