from rest_framework.serializers import ModelSerializer

from accounts.models import Employee


class EmployeeListSerializer(ModelSerializer):
    """Serializer with minimal informations for employees list."""

    class Meta:
        model = Employee
        fields = (
            "last_name",
            "first_name",
            "department",
        )
