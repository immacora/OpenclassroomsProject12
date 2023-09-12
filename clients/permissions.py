from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission
from clients.models import Client


class IsSalesContact(BasePermission):
    """Grant access to client sales contact."""

    def has_permission(self, request, view):
        client_id = view.kwargs["client_id"]
        client = get_object_or_404(Client, client_id=client_id)

        if request.user.is_superuser:
            return True

        if request.user.employee == client.sales_contact:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        return obj.sales_contact == request.user.employee
