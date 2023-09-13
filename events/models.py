import uuid
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

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
    locations = models.ManyToManyField(
        Location, related_name="event_locations", blank=True
    )

    def __str__(self):
        return f"Événement {self.event_name} pour le client {self.contract.client} géré par {self.support_contact}"


@receiver(pre_delete, sender=Event)
def delete_linked_locations(sender, instance, **kwargs):
    """Delete event locations if they are not used elsewhere."""
    locations = instance.locations.all()
    for location in locations:
        if location.event_locations.count() == 1:
            if location.client_locations.count() == 0:
                location.delete()
