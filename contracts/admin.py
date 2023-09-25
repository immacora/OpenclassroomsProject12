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
    list_filter = ("is_signed",)
    search_fields = ("client__company_name",)
    readonly_fields = ("client", "created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        try:
            if obj.client.contract_requested is False:
                raise PermissionDenied("La création de contrat n'est pas demandée.")
            obj.save()
        except PermissionDenied as e:
            self.message_user(request, str(e), level="ERROR")
            return None

    def delete_model(self, request, obj):
        try:
            if obj.is_signed is True:
                raise PermissionDenied("Vous ne pouvez pas supprimer un contrat signé.")
            obj.delete()
        except PermissionDenied as e:
            self.message_user(request, str(e), level="ERROR")
            return None
