from django.contrib import admin
from django.core.exceptions import PermissionDenied

from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """Define admin model for contract model."""

    list_display = [
        "contract_description",
        "amount",
        "payment_due",
        "is_signed",
        "client",
        "created_at",
        "updated_at",
    ]
    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        try:
            if obj.client.contract_requested is False:
                raise PermissionDenied("La création de contrat n'est pas demandée.")
            obj.save()
        except PermissionDenied as e:
            self.message_user(request, str(e), level="ERROR")
            return None
