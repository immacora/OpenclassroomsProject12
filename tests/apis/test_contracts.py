from rest_framework import status
from django.urls import reverse

from contracts.models import Contract
from tests.factories import ContractFactory


class TestGetContracts:
    """
    GIVEN fixtures for contracts and employees with their associated users and tokens
    WHEN user tries to get all contracts
    THEN checks that the response is valid and data are displayed
    """

    def test_get_contracts_route_success_with_manager_employee(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a fixture for management employee with its valid token
        WHEN the contracts endpoint is requested (GET)
        THEN checks that response is 200 and datas are displayed
        """
        contracts = ContractFactory.create_batch(5)  # noqa: F841
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.get(reverse("clients"), headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert Contract.objects.count() == 5
        assert 5 == response.data["count"]
        assert len(response.data["results"]) == 5

    def test_get_contracts_route_success_with_sales_employee(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a fixture for sales employee with its valid token
        WHEN the contracts endpoint is requested (GET)
        THEN checks that response is 200 and datas are displayed
        """
        contracts = ContractFactory.create_batch(5)  # noqa: F841
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.get(reverse("clients"), headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert 5 == response.data["count"]
        assert len(response.data["results"]) == 5

    def test_get_contracts_route_success_with_support_employee(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a fixture for support employee with its valid token
        WHEN the contracts endpoint is requested (GET)
        THEN checks that response is 200 and datas are displayed
        """
        contracts = ContractFactory.create_batch(5)  # noqa: F841
        access_token = employees_users_with_tokens["support_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.get(reverse("clients"), headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert 5 == response.data["count"]
        assert len(response.data["results"]) == 5

    def test_get_contracts_route_failed_with_unauthorized(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN an invalid token
        WHEN the contracts endpoint is requested (GET)
        THEN checks that response is 401 and error message is displayed
        """
        contracts = ContractFactory.create_batch(5)  # noqa: F841
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.get(reverse("clients"), headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "token_not_valid" in response.data["code"]
