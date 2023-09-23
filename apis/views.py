from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken

from clients.permissions import IsSalesContact
from helpers.functions import update_sales_contact
from accounts.models import Employee
from clients.models import Client
from locations.models import Location
from contracts.models import Contract
from .serializers import (
    CreateEmployeeSerializer,
    CustomUserDetailSerializer,
    EmployeeListSerializer,
    EmployeeDetailSerializer,
    ClientListSerializer,
    ClientDetailSerializer,
    LocationDetailSerializer,
    ContractListSerializer,
    ContractDetailSerializer,
)
from .filters import ContractFilter

CustomUser = get_user_model()


class LogoutAPIView(GenericAPIView):
    """Endpoint to logout users and blacklisting tokens."""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.user_id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)


class EmployeeListAPIView(ListCreateAPIView):
    """Get Epic Events employee list and create employee account with his related user
    if the requesting user IsAuthenticated and is_staff (IsAdminUser)."""

    permission_classes = (IsAuthenticated, IsAdminUser)
    serializer_class = EmployeeListSerializer
    queryset = Employee.objects.all()
    search_fields = ["last_name", "department"]

    def post(self, request, *args, **kwargs):
        serializer = CreateEmployeeSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user_data = serializer.validated_data.pop("user")
            user = CustomUser.objects.create_user(**user_data)
            employee = Employee.objects.create(user=user, **serializer.validated_data)
            employee_data = EmployeeDetailSerializer(employee).data

            return Response(employee_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeDetailAPIView(RetrieveUpdateDestroyAPIView):
    """
    Get Epic Events employee detail with his related user via id.
    Edit employee and their is_active user account and email.
    Delete employee and his user account.

    Permission : requesting user IsAuthenticated and is_staff (IsAdminUser).
    """

    permission_classes = (IsAuthenticated, IsAdminUser)
    serializer_class = EmployeeDetailSerializer

    def get_object(self):
        employee_id = self.kwargs["employee_id"]
        obj = get_object_or_404(Employee, employee_id=employee_id)
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        data = request.data

        if "user" in data:
            user_data = data.pop("user")
            user_serializer = CustomUserDetailSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user_to_update = instance.user

            if "is_active" in user_data:
                user_to_update.is_active = user_data["is_active"]

            if "email" in user_data:
                user_to_update.email = user_data["email"]

            user_to_update.save()

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class ClientListAPIView(ListCreateAPIView):
    """
    Get Epic Events client list (permission all authenticated employees).
    Create client if the requesting user IsAuthenticated and has add_client permission.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ClientListSerializer
    queryset = Client.objects.all()
    filterset_fields = ["contract_requested"]
    search_fields = ["company_name"]

    def post(self, request, *args, **kwargs):
        if request.user.has_perm("clients.add_client"):
            serializer = ClientDetailSerializer(
                context={"request": request}, data=request.data
            )
            if serializer.is_valid(raise_exception=True):
                author_user = serializer.validated_data.pop("sales_contact")
                client = Client.objects.create(
                    sales_contact=author_user.employee, **serializer.validated_data
                )
                client_data = ClientDetailSerializer(client).data
                return Response(client_data, status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST, *args, **kwargs
            )
        return Response(
            {"detail": "Vous n'avez pas la permission d'effectuer cette action."},
            status=status.HTTP_403_FORBIDDEN,
        )


class ClientDetailAPIView(RetrieveUpdateDestroyAPIView):
    """
    Get Epic Events client detail with their related locations via id.
    Edit client informations (MANAGEMENT and sales_contact) or update sales_contact (MANAGEMENT only).
    Delete client if there is no signed contracts.

    Permission : requesting user authenticated and IsAdminUser or IsSalesContact.
    """

    permission_classes = [IsAdminUser | IsAuthenticated & IsSalesContact]
    serializer_class = ClientDetailSerializer

    def get_object(self):
        client_id = self.kwargs["client_id"]
        obj = get_object_or_404(Client, client_id=client_id)
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        data = request.data

        if request.user.is_staff:
            if "updated_sales_contact" in data:
                updated_sales_contact_id = data["updated_sales_contact"]
                updated_sales_contact = update_sales_contact(
                    instance, updated_sales_contact_id
                )
                if not isinstance(updated_sales_contact, str):
                    return Response(updated_sales_contact, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"details": updated_sales_contact},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            return Response(
                {"details": "La saisie est invalide."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.has_signed_contracts():
            return Response(
                {
                    "details": "Vous ne pouvez pas supprimer un client dont au moins un contrat est signé."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            return self.destroy(request, *args, **kwargs)


class ClientLocationsListAPIView(ListCreateAPIView):
    """
    Get locations client list.
    Create or add location(s) to client.

    Permission : requesting user authenticated and IsAdminUser or IsSalesContact.
    """

    permission_classes = [IsAdminUser | IsAuthenticated & IsSalesContact]
    serializer_class = LocationDetailSerializer

    def list(self, request, *args, **kwargs):
        client_id = kwargs["client_id"]
        client = get_object_or_404(Client, client_id=client_id)
        queryset = client.locations.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        client_id = kwargs["client_id"]
        client = get_object_or_404(Client, client_id=client_id)
        locations_data = request.data.get("locations", [])
        locations_added = []

        for location_data in locations_data:
            serializer = self.serializer_class(data=location_data)

            if serializer.is_valid(raise_exception=True):
                location, created = Location.objects.get_or_create(
                    **serializer.validated_data
                )
                client.locations.add(location)
                locations_added.append(location)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        locations_serializer = LocationDetailSerializer(locations_added, many=True)
        return Response(data=locations_serializer.data, status=status.HTTP_201_CREATED)


class ClientLocationDetailAPIView(RetrieveUpdateDestroyAPIView):
    """
    Get client location detail.
    Edit and delete location if it is not in use by another client or event or remove it.

    Permission : requesting user authenticated and IsAdminUser or IsSalesContact.
    """

    permission_classes = [IsAdminUser | IsAuthenticated & IsSalesContact]
    serializer_class = LocationDetailSerializer

    def get_object(self):
        client_id = self.kwargs["client_id"]
        client = get_object_or_404(Client, client_id=client_id)
        location_id = self.kwargs["location_id"]
        obj = get_object_or_404(Location, location_id=location_id)
        self.check_object_permissions(self.request, client)
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid(raise_exception=True):
            if (
                instance.client_locations.count() == 1
                and instance.event_locations.count() == 0
            ):
                self.perform_update(serializer)
                return Response(serializer.data)
            return Response(
                {
                    "details": "Ce lieu est utilisé par un autre modèle. Vous devez le supprimer de ce modèle."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if (
            instance.client_locations.count() == 1
            and instance.event_locations.count() == 0
        ):
            return self.destroy(request, *args, **kwargs)
        client_id = kwargs["client_id"]
        client = get_object_or_404(Client, client_id=client_id)
        client.locations.remove(instance.location_id)
        return Response(
            {"details": "Le lieu a été retiré de ce client."}, status=status.HTTP_200_OK
        )


class ContractListAPIView(ListAPIView):
    """Get contracts list."""

    permission_classes = (IsAuthenticated,)
    serializer_class = ContractListSerializer
    queryset = Contract.objects.all()
    filterset_class = ContractFilter


class ClientContractsListAPIView(ListCreateAPIView):
    """
    Get contracts client list (permission authenticated IsAdminUser or IsSalesContact).
    Create contract if the requesting user IsAdminUser and if contract_requested client field is True.
    """

    permission_classes = [IsAdminUser | IsAuthenticated & IsSalesContact]
    serializer_class = ContractListSerializer
    filterset_fields = ["contract_requested"]

    def list(self, request, *args, **kwargs):
        client_id = kwargs["client_id"]
        queryset = Contract.objects.filter(client_id=client_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            client_id = kwargs["client_id"]
            client = get_object_or_404(Client, client_id=client_id)

            if client.contract_requested:
                serializer = ContractDetailSerializer(data=request.data)

                if serializer.is_valid(raise_exception=True):
                    payment_due = request.data["amount"]
                    contract = Contract.objects.create(
                        payment_due=payment_due,
                        client=client,
                        **serializer.validated_data
                    )
                    client.contract_requested = False
                    client.save()
                    contract_data = ContractDetailSerializer(contract).data
                    return Response(contract_data, status=status.HTTP_201_CREATED)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {"details": "La création de contrat n'est pas demandée."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detail": "Vous n'avez pas la permission d'effectuer cette action."},
            status=status.HTTP_403_FORBIDDEN,
        )
