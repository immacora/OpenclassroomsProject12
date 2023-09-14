import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from faker import Faker

from accounts.models import Employee

fake = Faker()
CustomUser = get_user_model()


class TestCreateUsers:
    """
    GIVEN a new_custom_user fixture
    WHEN user is created
    THEN checks that his permissions are ok
    """

    def test_create_default_user(self, new_custom_user):
        """
        Tests if default user creation :
            is True for is_active,
            is False for is_staff and is_superuser,
            does not have permission.
        """
        assert CustomUser.objects.count() == 1
        assert new_custom_user.email is not None
        assert new_custom_user.is_active
        assert new_custom_user.is_staff is False
        assert new_custom_user.is_superuser is False
        assert new_custom_user.get_all_permissions() == set()

    def test_create_user_with_not_unique_email_raises_error(self, new_custom_user):
        """Tests if user creation raise IntegrityError with not unique email."""
        with pytest.raises(IntegrityError):
            CustomUser.objects.create(
                email=new_custom_user.email, password="123456789!"
            )

    def test_create_superuser(self, new_superuser):
        """Tests if superuser creation has an email and is True for is_active, is_staff and is_superuser."""
        assert CustomUser.objects.count() == 1
        assert new_superuser.email is not None
        assert new_superuser.is_active
        assert new_superuser.is_staff
        assert new_superuser.is_superuser


class TestEmployees:
    def test_create_management_employee(self, new_employee):
        """
        Tests if MANAGEMENT employee creation :
            is True for staff and False for superuser,
            add user to group management,
            has a user who has the default following permissions.
        """
        assert Employee.objects.count() == 1
        assert CustomUser.objects.count() == 1
        assert new_employee.department == "MANAGEMENT"
        assert new_employee.user.is_staff
        assert new_employee.user.is_superuser is False
        assert str(new_employee.user.groups.get()) == "management"
        assert new_employee.user.get_all_permissions() == {
            "accounts.add_customuser",
            "accounts.change_customuser",
            "accounts.view_customuser",
            "accounts.add_employee",
            "accounts.change_employee",
            "accounts.delete_employee",
            "accounts.view_employee",
            "locations.view_location",
            "clients.change_client",
            "clients.delete_client",
            "clients.view_client",
            "contracts.add_contract",
            "contracts.change_contract",
            "contracts.view_contract",
            "events.change_event",
            "events.view_event",
        }

    def test_create_sales_employee(self, new_employee):
        """
        Tests if SALES employee creation :
            is False for staff and superuser,
            add user to group sales,
            has a user who has the default following permissions.
        """
        assert Employee.objects.count() == 1
        assert CustomUser.objects.count() == 1
        assert new_employee.department == "SALES"
        assert new_employee.user.is_staff is False
        assert new_employee.user.is_superuser is False
        assert str(new_employee.user.groups.get()) == "sales"
        assert new_employee.user.get_all_permissions() == {
            "locations.add_location",
            "locations.change_location",
            "locations.delete_location",
            "locations.view_location",
            "clients.add_client",
            "clients.view_client",
            "contracts.view_contract",
            "events.view_event",
        }

    def test_create_support_employee(self, new_employee):
        """
        Tests if SUPPORT employee creation :
            is False for staff and superuser,
            add user to group support,
            has a user who has the default following permissions.
        """
        assert Employee.objects.count() == 1
        assert CustomUser.objects.count() == 1
        assert new_employee.department == "SUPPORT"
        assert new_employee.user.is_staff is False
        assert new_employee.user.is_superuser is False
        assert str(new_employee.user.groups.get()) == "support"
        assert new_employee.user.get_all_permissions() == {
            "locations.add_location",
            "locations.change_location",
            "locations.delete_location",
            "locations.view_location",
            "clients.view_client",
            "contracts.view_contract",
            "events.view_event",
        }

    def test_create_employee_with_not_unique_number_raises_error(
        self, new_employee, new_custom_user
    ):
        """Tests if employee creation raise IntegrityError with not unique number."""
        with pytest.raises(IntegrityError):
            Employee.objects.create(
                employee_number=new_employee.employee_number,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                department="SALES",
                user=new_custom_user,
            )

    def test_create_employees_with_same_user_raises_error(self, new_employee):
        """Tests if employees creation raise IntegrityError with the same user."""
        with pytest.raises(IntegrityError):
            Employee.objects.create(
                employee_number=4578,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                department="SALES",
                user=new_employee.user,
            )

    def test_delete_employee_and_his_user(self, new_employee):
        """Tests if employees deletion delete his linked user.."""

        new_employee.delete()
        assert Employee.objects.count() == 0
        assert CustomUser.objects.count() == 0
