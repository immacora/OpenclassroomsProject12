from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken

from helpers.functions import add_locations_to_model
from clients.models import Client
from accounts.models import Employee
from .serializers import (
    CreateEmployeeSerializer,
    CustomUserDetailSerializer,
    EmployeeListSerializer,
    EmployeeDetailSerializer,
    ClientListSerializer,
    ClientDetailSerializer,
)

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
    Create client, their location(s) and sales_contact to which is added the change_client permission
    if the requesting user IsAuthenticated and has add_client permission.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ClientListSerializer
    queryset = Client.objects.all()

    def post(self, request, *args, **kwargs):
        if request.user.has_perm("clients.add_client"):
            serializer = ClientDetailSerializer(
                context={"request": request}, data=request.data
            )
            if serializer.is_valid(raise_exception=True):
                location_data = serializer.validated_data.pop("locations")
                author_user = serializer.validated_data.pop("sales_contact")
                client = Client.objects.create(
                    sales_contact=author_user.employee, **serializer.validated_data
                )
                add_locations_to_model(client, location_data)
                client_data = ClientDetailSerializer(client).data

                return Response(client_data, status=status.HTTP_201_CREATED)

            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST, *args, **kwargs
            )
        return Response(
            {"details": "Vous n'avez pas la permission d'effectuer cette action."},
            status=status.HTTP_403_FORBIDDEN,
        )
