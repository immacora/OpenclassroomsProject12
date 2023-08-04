from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Employee

CustomUser = get_user_model()


class CustomUserTests(TestCase):
    """Test user creation."""

    def setUp(self):
        self.password = "123456789!"

    def test_create_user(self):
        """Tests if default user creation is False for staff and superuser."""

        user = CustomUser.objects.create_user(email="testcreateuser@email.com", password=self.password)
        self.assertEqual(user.email, "testcreateuser@email.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Tests if default superuser creation is True for staff and superuser."""

        admin_user = CustomUser.objects.create_superuser(email="testcreatesuperuser@email.com", password=self.password)
        self.assertEqual(admin_user.email, "testcreatesuperuser@email.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)


class EmployeeTests(TestCase):
    """Test employee creation and deletion."""

    def setUp(self):
        self.password = "123456789!"
        self.first_name = "Employé test prénom"
        self.last_name = "Employé test nom"

        self.user_admin = CustomUser.objects.create(
            email="user_admin@test.com",
            password=self.password,
        )
        self.user_sales = CustomUser.objects.create(
            email="user_sales@test.com",
            password=self.password,
        )
        self.user_support = CustomUser.objects.create(
            email="user_support@test.com", password=self.password
        )
        self.management_employee = Employee.objects.create(
            employee_number="1",
            first_name=self.first_name,
            last_name=self.last_name,
            department="MANAGEMENT",
            user=self.user_admin,
        )
        self.sales_employee = Employee.objects.create(
            employee_number="2",
            first_name=self.first_name,
            last_name=self.last_name,
            department="SALES",
            user=self.user_sales,
        )
        self.support_employee = Employee.objects.create(
            employee_number="3",
            first_name=self.first_name,
            last_name=self.last_name,
            department="SUPPORT",
            user=self.user_support,
        )

    def test_create_management_employee(self):
        """Tests if MANAGEMENT employee creation is True for staff and False for superuser."""
        self.assertEqual(f"{self.management_employee.employee_number}", "1")
        self.assertEqual(f"{self.management_employee.first_name}", self.first_name)
        self.assertEqual(f"{self.management_employee.last_name}", self.last_name)
        self.assertEqual(f"{self.management_employee.department}", "MANAGEMENT")
        self.assertTrue(self.user_admin.is_active)
        self.assertTrue(self.user_admin.is_staff)
        self.assertFalse(self.user_admin.is_superuser)

    def test_create_sales_employee(self):
        """Tests if SALES employee creation is False for staff and superuser."""
        self.assertEqual(f"{self.sales_employee.employee_number}", "2")
        self.assertEqual(f"{self.sales_employee.first_name}", self.first_name)
        self.assertEqual(f"{self.sales_employee.last_name}", self.last_name)
        self.assertEqual(f"{self.sales_employee.department}", "SALES")
        self.assertTrue(self.user_sales.is_active)
        self.assertFalse(self.user_sales.is_staff)
        self.assertFalse(self.user_sales.is_superuser)

    def test_create_support_employee(self):
        """Tests if SUPPORT employee creation is False for staff and superuser."""
        self.assertEqual(f"{self.support_employee.employee_number}", "3")
        self.assertEqual(f"{self.support_employee.first_name}", self.first_name)
        self.assertEqual(f"{self.support_employee.last_name}", self.last_name)
        self.assertEqual(f"{self.support_employee.department}", "SUPPORT")
        self.assertTrue(self.user_support.is_active)
        self.assertFalse(self.user_support.is_staff)
        self.assertFalse(self.user_support.is_superuser)
