from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Define admin model for event model."""

    list_display = [
        "event_name",
        "start_date",
        "end_date",
        "attendees",
        "notes",
        "contract",
        "support_contact",
        "created_at",
        "updated_at",
    ]
    list_filter = ("start_date",)
    search_fields = ("support_contact__last_name",)
    readonly_fields = ("contract", "created_at", "updated_at")

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_event_over:
            return False
        return True
