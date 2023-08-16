from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from accounts.models import Employee
from .serializers import (
    EmployeeListSerializer,
)


class EmployeeListAPIView(ListCreateAPIView):
    """
    Get Epic Events employee list if user IsAuthenticated and is_staff (IsAdminUser).
    """

    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = EmployeeListSerializer
    queryset = Employee.objects.all()
