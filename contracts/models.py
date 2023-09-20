import uuid
from django.db import models

from clients.models import Client
from helpers.models import TimestampedModel
from helpers.validators import textfieldvalidator


class Contract(TimestampedModel):
    """Contract between Epic Events and client."""

    contract_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract_description = models.TextField(
        "Résumé du contrat",
        max_length=2000,
        blank=True,
        validators=[textfieldvalidator],
    )
    amount = models.FloatField("Montant de la prestation", blank=True, null=True)
    payment_due = models.FloatField("Reste à payer", blank=True, null=True)
    is_signed = models.BooleanField("Signé", default=False)
    client = models.ForeignKey(
        to=Client,
        on_delete=models.CASCADE,
        verbose_name="Client",
    )

    class Meta:
        ordering = ["is_signed"]

    def __str__(self):
        return f"Contrat du client {self.client}"
