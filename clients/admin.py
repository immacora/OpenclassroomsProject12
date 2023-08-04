from django.contrib import admin

from .models import Client


class ClientAdmin(admin.ModelAdmin):
    """Define admin model for client model."""

    list_display = [
        "company_name",
        "siren",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "sales_contact",
        "created_at",
        "updated_at",
    ]
    readonly_fields = ("created_at", "updated_at")


admin.site.register(Client, ClientAdmin)
