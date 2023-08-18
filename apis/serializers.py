from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, CharField, ValidationError

from accounts.models import Employee

CustomUser = get_user_model()


class CreateCustomUserSerializer(ModelSerializer):
    """Serializer to create a custom user."""

    password = CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )
    password2 = CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )

    class Meta:
        model = CustomUser
        fields = ("email", "password", "password2")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise ValidationError({"password": "Password fields didn't match."})
        attrs.pop("password2")
        return attrs


class CreateEmployeeSerializer(ModelSerializer):
    """Serializer to create Epic Events employees associated with CustomUser."""

    user = CreateCustomUserSerializer()

    class Meta:
        model = Employee
        fields = (
            "employee_number",
            "last_name",
            "first_name",
            "department",
            "user",
            "created_at",
            "updated_at",
        )


class CustomUserDetailSerializer(ModelSerializer):
    """Serializer with all custom user informations for creation verification."""

    class Meta:
        model = CustomUser
        fields = ("email", "is_active", "is_staff", "date_joined")
        read_only__fields = "is_staff", "date_joined"


class EmployeeDetailSerializer(ModelSerializer):
    """Serializer with all informations for Epic Events employees detail."""

    user = CustomUserDetailSerializer()

    class Meta:
        model = Employee
        fields = (
            "employee_number",
            "last_name",
            "first_name",
            "department",
            "user",
            "created_at",
            "updated_at",
        )


class CustomUserListSerializer(ModelSerializer):
    """Serializer with email only for custom user identification."""

    class Meta:
        model = CustomUser
        fields = ("email",)


class EmployeeListSerializer(ModelSerializer):
    """Serializer with minimal informations for employees list."""

    user = CustomUserListSerializer()

    class Meta:
        model = Employee
        fields = (
            "last_name",
            "first_name",
            "department",
            "user",
        )
