import pytest
from pytest_factoryboy import register
from tests.factories import (
    CustomUserFactory,
    EmployeeFactory,
    LocationFactory,
    SalesContactFactory,
    ClientFactory,
    ContractFactory,
    SupportContactFactory,
    EventFactory,
)
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

register(CustomUserFactory)
register(EmployeeFactory)
register(LocationFactory)
register(SalesContactFactory)
register(ClientFactory)
register(ContractFactory)
register(SupportContactFactory)
register(EventFactory)


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
    employee_factory.department.reset()

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


@pytest.fixture
def new_location(db, location_factory):
    location = location_factory.create()
    return location


@pytest.fixture
def new_sales_contact(db, sales_contact_factory):
    sales_contact = sales_contact_factory.create()
    return sales_contact


@pytest.fixture
def new_support_contact(db, support_contact_factory):
    support_contact = support_contact_factory.create()
    return support_contact


@pytest.fixture
def new_client(db, client_factory):
    client = client_factory.create()
    refresh = RefreshToken.for_user(client.sales_contact.user)
    client.sales_contact.user.access_token = str(refresh.access_token)
    client.sales_contact.user.refresh_token = str(refresh)
    return client


@pytest.fixture
def new_client_with_location(db, client_factory, location_factory):
    client = client_factory.create()
    location = location_factory.create()
    client.locations.add(location)
    refresh = RefreshToken.for_user(client.sales_contact.user)
    client.sales_contact.user.access_token = str(refresh.access_token)
    client.sales_contact.user.refresh_token = str(refresh)
    return client


@pytest.fixture
def new_contract(db, contract_factory):
    contract = contract_factory.create()
    client_user = contract.client.sales_contact.user
    refresh = RefreshToken.for_user(client_user)
    client_user.access_token = str(refresh.access_token)
    client_user.refresh_token = str(refresh)
    return contract


@pytest.fixture
def new_event(db, event_factory):
    event = event_factory.create()
    event_user = event.support_contact.user
    refresh = RefreshToken.for_user(event_user)
    event_user.access_token = str(refresh.access_token)
    event_user.refresh_token = str(refresh)
    return event


@pytest.fixture
def new_event_with_location(db, event_factory, location_factory):
    event = event_factory.create()
    event_user = event.support_contact.user
    location = location_factory.create()
    event.locations.add(location)
    refresh = RefreshToken.for_user(event_user)
    event_user.access_token = str(refresh.access_token)
    event_user.refresh_token = str(refresh)
    return event
