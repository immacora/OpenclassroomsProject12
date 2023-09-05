from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken

from accounts.models import Employee
from .serializers import (
    EmployeeListSerializer,
    CreateEmployeeSerializer,
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
    """Get Epic Events employee list and create employee account if user IsAuthenticated and is_staff (IsAdminUser)."""

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
