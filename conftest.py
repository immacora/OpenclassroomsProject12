import pytest
from pytest_factoryboy import register
from tests.factories import CustomUserFactory, EmployeeFactory

register(CustomUserFactory)
register(EmployeeFactory)


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
