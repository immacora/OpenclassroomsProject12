from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission
from events.models import Event


class IsSupportContact(BasePermission):
    """Grant access to event support contact."""

    def has_permission(self, request, view):
        event_id = view.kwargs["event_id"]
        event = get_object_or_404(Event, event_id=event_id)

        if request.user.is_superuser:
            return True

        if request.user.employee == event.support_contact:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        return obj.support_contact == request.user.employee
