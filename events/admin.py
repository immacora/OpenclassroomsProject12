from django.contrib import admin

from .models import Event


class EventAdmin(admin.ModelAdmin):
    """Define admin model for Event model."""

    list_display = ["event_name", "start_date", "end_date", "attendees", "notes", "contract", "support_contact", "created_at", "updated_at"]
    readonly_fields = ("created_at", "updated_at")


admin.site.register(Event, EventAdmin)
