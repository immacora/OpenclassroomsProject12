import uuid
from django.utils import timezone
from django.core.exceptions import ValidationError
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

    @property
    def is_event_over(self):
        """Return True if events is over."""
        now = timezone.now()
        return self.end_date < now

    def __str__(self):
        return f"Événement {self.event_name} pour le client {self.contract.client.company_name}\
géré par {self.support_contact}"

    def clean(self):
        """Raise error if end_date is later than start_date and start_date is in past."""
        now = timezone.now()

        if self.start_date and self.start_date < now:
            raise ValidationError("La date de début ne peut pas être dans le passé.")

        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError(
                "La date de fin doit être postérieure à la date de début."
            )


@receiver(pre_delete, sender=Event)
def delete_linked_locations(sender, instance, **kwargs):
    """Delete event locations if they are not used by other clients or events."""
    locations = instance.locations.all()
    for location in locations:
        if location.event_locations.count() == 1:
            if location.client_locations.count() == 0:
                location.delete()
