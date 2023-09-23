import uuid
from rest_framework import status
from django.urls import reverse

from contracts.models import Contract


class TestGetClientContracts:
    """
    GIVEN fixtures for contract and employees with their associated users and tokens
    WHEN user tries to get client contracts
    THEN checks that the response is valid and data are displayed
    """

    def test_get_clients_contracts_route_success(self, api_client, new_contract):
        """
        GIVEN a fixture for contract with its client sales_contact valid token
        WHEN the contract endpoint is requested (GET)
        THEN checks that response is 200 and datas are displayed
        """
        access_token = new_contract.client.sales_contact.user.access_token
        client_id = new_contract.client.client_id
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.get(
            reverse("client_contracts", kwargs={"client_id": client_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert Contract.objects.count() == 1

    def test_get_clients_contracts_route_failed_with_forbidden(
        self, api_client, new_contract, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for contract and unassigned sales_contact valid token
        WHEN the contract endpoint is requested (GET)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        client_id = new_contract.client.client_id
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.get(
            reverse("client_contracts", kwargs={"client_id": client_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Contract.objects.count() == 1
        assert "count" not in response.data
        assert "results" not in response.data
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_get_clients_contracts_route_failed_with_unauthorized(
        self, api_client, new_contract
    ):
        """
        GIVEN a fixture for contract and an invalid token
        WHEN the contract endpoint is requested (GET)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        client_id = new_contract.client.client_id
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.get(
            reverse("client_contracts", kwargs={"client_id": client_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Contract.objects.count() == 1
        assert "count" not in response.data
        assert "results" not in response.data
        assert "token_not_valid" in response.data["code"]


class TestPostClientContracts:
    """
    GIVEN fixtures for client and employees with their associated users and tokens, valid and invalid contract data
    WHEN user tries to create a new contract
    THEN checks that the response is valid and data are displayed
    """

    valid_data = {
        "contract_description": "Nouveau contrat en attente.",
        "amount": 1068.25,
    }
    invalid_data = {"contract_description": "/", "amount": "WRONG"}

    def test_post_clients_contracts_route_success(
        self, api_client, new_client, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for client, management employee valid token and valid data
        WHEN the contract endpoint is posted to (POST)
        THEN checks that response is 201 and datas are displayed
        """
        new_client.contract_requested = True
        new_client.save()
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        client_id = new_client.client_id
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse("client_contracts", kwargs={"client_id": client_id}),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Contract.objects.count() == 1
        assert "contract_id" in response.data
        assert "Nouveau contrat en attente." in response.data["contract_description"]
        assert 1068.25 == float(response.data["amount"]) and float(
            response.data["payment_due"]
        )
        assert response.data["is_signed"] is False
        assert client_id == uuid.UUID(response.data["client"]["client_id"])
        assert response.data["created_at"] == response.data["updated_at"]

    def test_post_clients_contracts_route_failed_with_bad_request(
        self, api_client, new_client, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for client, management employee valid token and invalid data
        WHEN the contract endpoint is posted to (POST)
        THEN checks that response is 400 and error messages are displayed
        """
        new_client.contract_requested = True
        new_client.save()
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        client_id = new_client.client_id
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse("client_contracts", kwargs={"client_id": client_id}),
            headers=headers,
            data=self.invalid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Contract.objects.count() == 0
        assert (
            "La saisie ne doit pas comporter de caractères spéciaux."
            in response.data["contract_description"]
        )
        assert "Un nombre valide est requis." in response.data["amount"]

    def test_post_clients_contracts_route_failed_with_contract_not_required_bad_request(
        self, api_client, new_client, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for client, management employee valid token and valid data
        WHEN the contract endpoint is posted but contract is not required (POST)
        THEN checks that response is 400 and an error message is displayed
        """
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        client_id = new_client.client_id
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse("client_contracts", kwargs={"client_id": client_id}),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Contract.objects.count() == 0
        assert "La création de contrat n'est pas demandée." in response.data["details"]

    def test_post_clients_contracts_route_failed_with_forbidden(
        self, api_client, new_client
    ):
        """
        GIVEN a fixture for client, a not management valid token and valid data
        WHEN the contract endpoint is posted to (POST)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = new_client.sales_contact.user.access_token
        client_id = new_client.client_id
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse("client_contracts", kwargs={"client_id": client_id}),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Contract.objects.count() == 0
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_post_clients_contracts_failed_with_unauthorized(
        self, api_client, new_client
    ):
        """
        GIVEN a fixture for client, an invalid token and valid data
        WHEN the contract endpoint is posted to (POST)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        client_id = new_client.client_id
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse("client_contracts", kwargs={"client_id": client_id}),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Contract.objects.count() == 0
        assert "token_not_valid" in response.data["code"]
