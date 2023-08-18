from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from accounts.models import Employee
from .serializers import (
    EmployeeListSerializer,
    CreateEmployeeSerializer,
    EmployeeDetailSerializer
)

CustomUser = get_user_model()


class EmployeeListAPIView(ListCreateAPIView):
    """
    Get Epic Events employee list and create employee account if user IsAuthenticated and is_staff (IsAdminUser).
    """

    permission_classes = [IsAuthenticated, IsAdminUser]
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
