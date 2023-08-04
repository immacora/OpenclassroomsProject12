from django.contrib import admin

from .models import Contract


class ContractAdmin(admin.ModelAdmin):
    """Define admin model for contract model."""

    list_display = ["client", "amount", "payment_due", "is_signed", "created_at", "updated_at"]
    readonly_fields = ("created_at", "updated_at")


admin.site.register(Contract, ContractAdmin)
