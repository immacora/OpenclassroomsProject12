import uuid
from rest_framework import status
from django.urls import reverse

from contracts.models import Contract


class TestGetClientContract:
    """
    GIVEN fixtures for contract and employees with their associated users and tokens
    WHEN user tries to get client contract via id
    THEN checks that the response is valid and data are displayed
    """

    def test_get_client_contract_route_success(self, api_client, new_contract):
        """
        GIVEN a fixture for contract with its client sales_contact valid token
        WHEN the client_contract_detail endpoint is requested (GET)
        THEN checks that response is 200 and datas are displayed
        """
        access_token = new_contract.client.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_contract.client.client_id
        contract_id = new_contract.contract_id
        response = api_client.get(
            reverse(
                "client_contract_detail",
                kwargs={"client_id": client_id, "contract_id": contract_id},
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert Contract.objects.count() == 1
        assert contract_id == uuid.UUID(response.data["contract_id"])
        assert (
            new_contract.contract_description == response.data["contract_description"]
        )
        assert new_contract.amount == float(response.data["amount"])
        assert new_contract.payment_due == float(response.data["payment_due"])
        assert new_contract.is_signed is bool(response.data["is_signed"])
        assert new_contract.client.client_id == uuid.UUID(
            response.data["client"]["client_id"]
        )
        assert "created_at" in response.data
        assert "updated_at" in response.data

    def test_get_client_contract_route_failed_with_forbidden(
        self, api_client, new_contract, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for contract and valid unassigned sales contact token
        WHEN the client_contract_detail endpoint is requested (GET)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_contract.client.client_id
        contract_id = new_contract.contract_id
        response = api_client.get(
            reverse(
                "client_contract_detail",
                kwargs={"client_id": client_id, "contract_id": contract_id},
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Contract.objects.count() == 1
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_get_client_contract_route_failed_with_unauthorized(
        self, api_client, new_contract
    ):
        """
        GIVEN a fixture for contract and an invalid token
        WHEN the client_contract_detail endpoint is requested (GET)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_contract.client.client_id
        contract_id = new_contract.contract_id
        response = api_client.get(
            reverse(
                "client_contract_detail",
                kwargs={"client_id": client_id, "contract_id": contract_id},
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Contract.objects.count() == 1
        assert "token_not_valid" in response.data["code"]

    def test_get_client_contract_route_failed_with_not_found(
        self, api_client, new_contract
    ):
        """
        GIVEN a fixture for contract with its client sales_contact valid token
        WHEN the client_contract_detail endpoint is requested (GET)
        THEN checks that response is 404
        """
        access_token = new_contract.client.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_contract.client.client_id
        response = api_client.get(
            f"api/clients/{client_id}/contracts/INVALID_contract_id/", headers=headers
        )
        assert Contract.objects.count() == 1
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPutClientContract:
    """
    GIVEN fixtures for contract and employees with their associated users and tokens, valid and invalid contract data
    WHEN user tries to update contract location via id
    THEN checks that the response is valid and data are displayed
    """

    valid_data = {
        "contract_description": "UPDATED Contrat n°1 avec le client TEST.",
        "amount": "1452.25",
        "payment_due": "200",
        "is_signed": "True",
    }
    invalid_data = {
        "contract_description": "/",
        "amount": "WRONG",
        "payment_due": "WRONG",
        "is_signed": "WRONG",
    }

    def test_put_client_contract_route_success(self, api_client, new_contract):
        """
        GIVEN a fixture for contract with its client sales_contact valid token and valid data
        WHEN the client_contract_detail endpoint is updated to (PUT)
        THEN checks that response is 200 and datas are displayed
        """
        access_token = new_contract.client.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_contract.client.client_id
        contract_id = new_contract.contract_id
        response = api_client.put(
            reverse(
                "client_contract_detail",
                kwargs={"client_id": client_id, "contract_id": contract_id},
            ),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert Contract.objects.count() == 1
        assert contract_id == uuid.UUID(response.data["contract_id"])
        assert (
            "UPDATED Contrat n°1 avec le client TEST."
            in response.data["contract_description"]
        )
        assert 1452.25 == float(response.data["amount"])
        assert 200 == float(response.data["payment_due"])
        assert True is bool(response.data["is_signed"])
        assert response.data["created_at"] != response.data["updated_at"]

    def test_put_client_contract_route_failed_with_bad_request(
        self, api_client, new_contract
    ):
        """
        GIVEN a fixture for contract with its client sales_contact valid token and invalid data
        WHEN the client_contract_detail endpoint is updated to (PUT)
        THEN checks that response is 400 and error messages are displayed
        """
        access_token = new_contract.client.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_contract.client.client_id
        contract_id = new_contract.contract_id
        response = api_client.put(
            reverse(
                "client_contract_detail",
                kwargs={"client_id": client_id, "contract_id": contract_id},
            ),
            headers=headers,
            data=self.invalid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Contract.objects.count() == 1
        assert (
            "La saisie ne doit pas comporter de caractères spéciaux."
            in response.data["contract_description"]
        )
        assert "Un nombre valide est requis." in response.data["amount"]
        assert "Un nombre valide est requis." in response.data["payment_due"]
        assert "Must be a valid boolean." in response.data["is_signed"]

    def test_put_client_contract_route_failed_with_forbidden(
        self, api_client, new_contract, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for contract, valid unassigned sales_contact token and valid data
        WHEN the client_contract_detail endpoint is updated to (PUT)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_contract.client.client_id
        contract_id = new_contract.contract_id
        response = api_client.put(
            reverse(
                "client_contract_detail",
                kwargs={"client_id": client_id, "contract_id": contract_id},
            ),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Contract.objects.count() == 1
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_put_client_contract_failed_with_unauthorized(
        self, api_client, new_contract
    ):
        """
        GIVEN a fixture for contract, an invalid token and valid data
        WHEN the client_contract_detail endpoint is updated to (PUT)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_contract.client.client_id
        contract_id = new_contract.contract_id
        response = api_client.put(
            reverse(
                "client_contract_detail",
                kwargs={"client_id": client_id, "contract_id": contract_id},
            ),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Contract.objects.count() == 1
        assert "token_not_valid" in response.data["code"]


class TestDeleteClientContract:
    """
    GIVEN fixtures for contract and employees with their associated users and tokens
    WHEN user tries to delete a contract via id
    THEN checks that the response is valid or error message is displayed
    """

    def test_delete_client_contract_route_success(self, api_client, new_contract):
        """
        GIVEN a fixture for contract with its client sales_contact valid token
        WHEN the client_contract_detail endpoint is deleted (DEL)
        THEN checks that response is 204
        """
        access_token = new_contract.client.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_contract.client.client_id
        contract_id = new_contract.contract_id
        response = api_client.delete(
            reverse(
                "client_contract_detail",
                kwargs={"client_id": client_id, "contract_id": contract_id},
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Contract.objects.count() == 0

    def test_delete_client_contract_route_failed_with_bad_request(
        self, api_client, new_contract
    ):
        """
        GIVEN a fixture for contract with its client sales_contact valid token
        WHEN the client_contract_detail endpoint is deleted with is_signed contract (DEL)
        THEN checks that response is 400 and an error message is displayed
        """
        new_contract.is_signed = True
        new_contract.save()
        access_token = new_contract.client.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_contract.client.client_id
        contract_id = new_contract.contract_id
        response = api_client.delete(
            reverse(
                "client_contract_detail",
                kwargs={"client_id": client_id, "contract_id": contract_id},
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Contract.objects.count() == 1

    def test_delete_client_contract_route_failed_with_forbidden(
        self, api_client, new_contract, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for contract and valid unassigned sales contact with token
        WHEN the client_contract_detail endpoint is deleted (DEL)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_contract.client.client_id
        contract_id = new_contract.contract_id
        response = api_client.delete(
            reverse(
                "client_contract_detail",
                kwargs={"client_id": client_id, "contract_id": contract_id},
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Contract.objects.count() == 1
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_delete_client_contract_route_failed_with_unauthorized(
        self, api_client, new_contract
    ):
        """
        GIVEN a fixture for contract and invalid token
        WHEN the client_contract_detail endpoint is deleted (DEL)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_contract.client.client_id
        contract_id = new_contract.contract_id
        response = api_client.delete(
            reverse(
                "client_contract_detail",
                kwargs={"client_id": client_id, "contract_id": contract_id},
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Contract.objects.count() == 1
        assert "token_not_valid" in response.data["code"]
