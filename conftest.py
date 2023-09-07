import pytest
from pytest_factoryboy import register
from tests.factories import CustomUserFactory, EmployeeFactory
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

register(CustomUserFactory)
register(EmployeeFactory)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def new_custom_user(db, custom_user_factory):
    user = custom_user_factory.create()
    return user


@pytest.fixture
def new_superuser(db, custom_user_factory):
    superuser = custom_user_factory.create(is_staff=True, is_superuser=True)
    return superuser


@pytest.fixture
def new_employee(db, employee_factory):
    employee = employee_factory.create()
    return employee


@pytest.fixture
def employees_users_with_tokens(db, employee_factory):
    """Create an employee from each department with their associated access and refresh tokens for users."""

    management_employee = employee_factory.create()
    sales_employee = employee_factory.create()
    support_employee = employee_factory.create()

    for employee in [management_employee, sales_employee, support_employee]:
        refresh = RefreshToken.for_user(employee.user)
        employee.user.access_token = str(refresh.access_token)
        employee.user.refresh_token = str(refresh)

    return {
        "management_employee": management_employee,
        "sales_employee": sales_employee,
        "support_employee": support_employee,
    }
