from django.contrib import admin
from django.core.exceptions import PermissionDenied

from contracts.models import Contract
from .models import Client


class ContractInline(admin.TabularInline):
    model = Contract
    extra = 0
    fields = (
        "contract_description",
        "amount",
        "payment_due",
        "is_signed",
        "client",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Define admin model for client model."""

    inlines = [ContractInline]
    list_display = [
        "company_name",
        "siren",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "contract_requested",
        "sales_contact",
        "created_at",
        "updated_at",
    ]
    list_filter = ("contract_requested",)
    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        try:
            if not obj.sales_contact.department == "SALES":
                raise PermissionDenied(
                    "Le sales_contact doit être un employé du département ventes."
                )
            obj.save()
        except PermissionDenied as e:
            self.message_user(request, str(e), level="ERROR")
            return None

    def delete_model(self, request, obj):
        try:
            if obj.has_signed_contracts():
                raise PermissionDenied(
                    "Vous ne pouvez pas supprimer un client dont au moins un contrat est signé."
                )
            obj.delete()
        except PermissionDenied as e:
            self.message_user(request, str(e), level="ERROR")
            return None
