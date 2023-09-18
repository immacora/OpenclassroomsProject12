from django.contrib import admin
from django.core.exceptions import PermissionDenied

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Define admin model for client model."""

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
                raise PermissionDenied("Le sales_contact doit être un employé du département ventes.")
            obj.save()
        except PermissionDenied as e:
            self.message_user(request, str(e), level='ERROR')
            return None
