from django.contrib import admin

from events.models import Event
from .models import Contract


class EventInline(admin.TabularInline):
    """
    Add inline event to contract model.
    Can add one event if contract is_signed.
    Can udate or delete contract via change link.
    """

    model = Event
    extra = 0
    fields = (
        "event_name",
        "start_date",
        "end_date",
        "attendees",
        "notes",
        "contract",
        "support_contact",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("contract", "created_at", "updated_at")
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj):
        return obj.is_signed


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """Define admin model for contract model."""

    inlines = [EventInline]
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

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_signed:
            return False
        return True

    def has_change_permission(self, request, obj=None):
        if obj and obj.event and obj.event.is_event_over:
            return False
        return True
