from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken

from accounts.models import Employee
from .serializers import (
    CreateEmployeeSerializer,
    EmployeeListSerializer,
    EmployeeDetailSerializer,
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
            user_to_update = instance.user

            if "is_active" in user_data:
                new_user_status = user_data["is_active"]
                try:
                    user_to_update.is_active = new_user_status
                    user_to_update.save()
                except ValidationError as e:
                    return Response({"details": e}, status=status.HTTP_400_BAD_REQUEST)
            if "email" in user_data:
                new_user_email = user_data["email"]

                if user_to_update.email != new_user_email:
                    try:
                        validate_email(new_user_email)
                    except ValidationError as e:
                        return Response(
                            {"details": e}, status=status.HTTP_400_BAD_REQUEST
                        )
                    else:
                        if CustomUser.objects.filter(email=new_user_email).exists():
                            return Response(
                                {"message": "Cette adresse email est déjà attribuée."},
                                status=status.HTTP_409_CONFLICT,
                            )
                        else:
                            user_to_update.email = new_user_email
                            user_to_update.save()

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
