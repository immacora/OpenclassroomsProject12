from django.contrib import admin

from contracts.models import Contract
from .models import Client


class ContractInline(admin.TabularInline):
    """
    Add inline contract to client model.
    Can add contract if contract_requested is true.
    Can update or delete contract via change link.
    """

    model = Contract
    extra = 0
    fields = (
        "contract_description",
        "amount",
        "payment_due",
        "is_signed",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj):
        return obj.contract_requested


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

    def has_delete_permission(self, request, obj=None):
        if obj and hasattr(obj, "has_signed_contracts") and obj.has_signed_contracts():
            return False
        return True
