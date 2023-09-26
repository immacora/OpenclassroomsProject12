from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    ValidationError,
    UUIDField,
    CurrentUserDefault,
)

from accounts.models import Employee
from locations.models import Location
from clients.models import Client
from contracts.models import Contract
from events.models import Event

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
        fields = ("user_id", "email", "password", "password2")

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
            "employee_id",
            "employee_number",
            "last_name",
            "first_name",
            "department",
            "user",
            "created_at",
            "updated_at",
        )
        read_only__fields = ("employee_id", "created_at", "updated_at")


class CustomUserDetailSerializer(ModelSerializer):
    """Serializer with all custom user informations."""

    class Meta:
        model = CustomUser
        fields = ("user_id", "email", "is_active", "is_staff", "date_joined")
        read_only__fields = ("user_id", "is_staff", "date_joined")


class EmployeeDetailSerializer(ModelSerializer):
    """Serializer with all Epic Events employee informations."""

    user = CustomUserDetailSerializer()

    class Meta:
        model = Employee
        fields = (
            "employee_id",
            "employee_number",
            "last_name",
            "first_name",
            "department",
            "user",
            "created_at",
            "updated_at",
        )
        read_only__fields = ("employee_id", "created_at", "updated_at")


class CustomUserListSerializer(ModelSerializer):
    """Serializer with email only for custom user identification."""

    class Meta:
        model = CustomUser
        fields = (
            "user_id",
            "email",
        )
        read_only__fields = ("user_id",)


class EmployeeListSerializer(ModelSerializer):
    """Serializer with minimal informations for employees list."""

    user = CustomUserListSerializer()

    class Meta:
        model = Employee
        fields = (
            "employee_id",
            "last_name",
            "first_name",
            "department",
            "user",
        )
        read_only__fields = ("employee_id",)


class LocationDetailSerializer(ModelSerializer):
    """Serializer with all location informations."""

    class Meta:
        model = Location
        fields = (
            "location_id",
            "street_number",
            "street_name",
            "city",
            "zip_code",
            "country",
        )
        read_only__fields = ("location_id",)


class ClientDetailSerializer(ModelSerializer):
    """
    Serializer with all client informations including location.
    Assigns the default sales_contact (logged-in user) during creation.
    Update sales_contact (MANAGEMENT ONLY) with updated_sales_contact write_only field.
    """

    sales_contact = UUIDField(default=CurrentUserDefault())
    updated_sales_contact = UUIDField(write_only=True, required=False)

    class Meta:
        model = Client
        fields = (
            "client_id",
            "company_name",
            "siren",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "contract_requested",
            "sales_contact",
            "updated_sales_contact",
            "locations",
            "created_at",
            "updated_at",
        )
        read_only__fields = ("client_id", "sales_contact", "created_at", "updated_at")


class EmployeeStrSerializer(ModelSerializer):
    """Serializer with __str__ informations for other models list."""

    representation_str = CharField(source="__str__", read_only=True)

    class Meta:
        model = Employee
        fields = ["representation_str"]


class ClientListSerializer(ModelSerializer):
    """Serializer with minimal informations for clients list."""

    sales_contact = EmployeeStrSerializer()

    class Meta:
        model = Client
        fields = (
            "client_id",
            "company_name",
            "siren",
            "sales_contact",
            "contract_requested",
            "created_at",
            "updated_at",
        )
        read_only__fields = ("client_id", "created_at", "updated_at")


class ContractDetailSerializer(ModelSerializer):
    """Serializer with all contract informations."""

    client = ClientListSerializer(required=False)

    class Meta:
        model = Contract
        fields = (
            "contract_id",
            "contract_description",
            "amount",
            "payment_due",
            "is_signed",
            "client",
            "created_at",
            "updated_at",
        )
        read_only__fields = ("contract_id", "client", "created_at", "updated_at")


class ClientStrSerializer(ModelSerializer):
    """Serializer with __str__ information for other models list."""

    representation_str = CharField(source="__str__", read_only=True)

    class Meta:
        model = Client
        fields = ["representation_str"]


class ContractListSerializer(ModelSerializer):
    """Serializer with minimal informations for contracts list."""

    client = ClientStrSerializer()

    class Meta:
        model = Contract
        fields = (
            "contract_id",
            "is_signed",
            "amount",
            "payment_due",
            "client",
            "created_at",
            "updated_at",
        )
        read_only__fields = ("contract_id", "created_at", "updated_at")


class EventDetailSerializer(ModelSerializer):
    """Serializer with all event informations."""

    contract = ContractListSerializer(required=False)

    class Meta:
        model = Event
        fields = (
            "event_id",
            "event_name",
            "start_date",
            "end_date",
            "attendees",
            "notes",
            "contract",
            "support_contact",
            "locations",
        )
        read_only__fields = ("event_id", "contract", "created_at", "updated_at")


class EventListSerializer(ModelSerializer):
    """Serializer with minimal informations for events list."""

    support_contact = EmployeeStrSerializer()

    class Meta:
        model = Event
        fields = (
            "event_id",
            "event_name",
            "start_date",
            "end_date",
            "is_event_over",
            "contract",
            "support_contact",
        )
        read_only__fields = ("event_id", "contract", "created_at", "updated_at")
