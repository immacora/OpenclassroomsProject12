import uuid
from django.db import models

from contracts.models import Contract
from accounts.models import Employee
from locations.models import Location
from helpers.models import TimestampedModel
from helpers.validators import unicodecharfieldvalidator, textfieldvalidator


class Event(TimestampedModel):
    """Event related to the contract between Epic Events and its client."""

    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_name = models.CharField(
        "Nom de l'événement",
        max_length=150,
        blank=True,
        validators=[unicodecharfieldvalidator],
    )
    start_date = models.DateTimeField("Date de début de l'événement")
    end_date = models.DateTimeField("Date de fin de l'événement")
    attendees = models.PositiveSmallIntegerField("Nombre de participants")
    notes = models.TextField(
        "Notes sur l'événement",
        max_length=2000,
        blank=True,
        validators=[textfieldvalidator],
    )
    contract = models.OneToOneField(
        to=Contract, on_delete=models.CASCADE, verbose_name="contrat"
    )
    support_contact = models.ForeignKey(
        to=Employee,
        on_delete=models.SET_NULL,
        verbose_name="Support",
        null=True,
        blank=True,
    )
    locations = models.ManyToManyField(Location)

    def __str__(self):
        return f"Événement {self.event_name} pour le client {self.contract.client} géré par {self.support_contact}"
