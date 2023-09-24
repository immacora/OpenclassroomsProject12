import uuid
from rest_framework import status
from django.urls import reverse

from clients.models import Client
from locations.models import Location


class TestGetClient:
    """
    GIVEN fixtures for client and employees with their associated users and tokens
    WHEN user tries to get client via id
    THEN checks that the response is valid and data are displayed
    """

    def test_get_client_route_success(self, api_client, new_client):
        """
        GIVEN a fixture for client with its sales_contact valid token
        WHEN the client endpoint is requested (GET)
        THEN checks that response is 200 and datas are displayed
        """
        access_token = new_client.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client.client_id
        response = api_client.get(
            reverse("client_detail", kwargs={"client_id": client_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert Client.objects.count() == 1
        assert client_id == uuid.UUID(response.data["client_id"])
        assert new_client.company_name == response.data["company_name"]
        assert new_client.siren == response.data["siren"]
        assert new_client.last_name in response.data["last_name"]
        assert new_client.first_name in response.data["first_name"]
        assert new_client.email in response.data["email"]
        assert str(new_client.phone_number) in response.data["phone_number"]
        assert (
            response.data["contract_requested"] is True
            or response.data["contract_requested"] is False
        )
        assert "SALES" in response.data["sales_contact"]
        assert "created_at" in response.data
        assert "updated_at" in response.data

    def test_get_client_route_failed_with_forbidden(
        self, api_client, new_client, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for client and valid unassigned sales contact token
        WHEN the client endpoint is requested (GET)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client.client_id
        response = api_client.get(
            reverse("client_detail", kwargs={"client_id": client_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Client.objects.count() == 1
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_get_client_route_failed_with_unauthorized(self, api_client, new_client):
        """
        GIVEN a fixture for client and an invalid token
        WHEN the client endpoint is requested (GET)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client.client_id
        response = api_client.get(
            reverse("employee_detail", kwargs={"employee_id": client_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Client.objects.count() == 1
        assert "token_not_valid" in response.data["code"]

    def test_get_client_route_failed_with_not_found(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a fixture for sales employee with valid token and an invalid client_id
        WHEN the client endpoint is requested (GET)
        THEN checks that response is 404
        """
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.get("api/clients/1234/", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPutClient:
    """
    GIVEN fixtures for client and employees with their associated users and tokens, and valid client data
    WHEN user tries to update client and sales_contact
    THEN checks that the response is valid and data are displayed
    """

    valid_client_data = {
        "company_name": "UPDATED Entreprise TEST",
        "siren": "111111111",
        "first_name": "UPDATED Prénom du client TEST",
        "last_name": "UPDATED Nom du client TEST",
        "email": "UPDATEDclientTEST@email.com",
        "phone_number": "+33600000000",
        "contract_requested": "True",
    }

    def test_put_client_informations_route_success(self, api_client, new_client):
        """
        GIVEN a fixture for client with its sales_contact valid token and valid client data
        WHEN the client endpoint is updated to (PUT)
        THEN checks that response is 200 and datas are displayed
        """
        access_token = new_client.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client.client_id
        response = api_client.put(
            reverse("client_detail", kwargs={"client_id": client_id}),
            headers=headers,
            data=self.valid_client_data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert Client.objects.count() == 1
        assert client_id == uuid.UUID(response.data["client_id"])
        assert "UPDATED Entreprise TEST" in response.data["company_name"]
        assert 111111111 == int(response.data["siren"])
        assert "UPDATED Prénom du client TEST" in response.data["first_name"]
        assert "UPDATED Nom du client TEST" in response.data["last_name"]
        assert "UPDATEDclientTEST@email.com" in response.data["email"]
        assert "+33600000000" == response.data["phone_number"]
        assert response.data["contract_requested"] is True
        assert new_client.sales_contact.last_name in response.data["sales_contact"]
        assert response.data["created_at"] != response.data["updated_at"]

    def test_put_client_informations_route_failed_with_bad_request(
        self, api_client, new_client
    ):
        """
        GIVEN a fixture for client with its sales_contact valid token and invalid client data
        WHEN the client endpoint is updated to (PUT)
        THEN checks that response is 400 and error messages are displayed
        """
        invalid_client_data = {
            "company_name": "/Entreprise TEST",
            "siren": "WRONG",
            "first_name": ",Prénom du client TEST",
            "last_name": "!Nom du client TEST",
            "email": "WRONG",
            "phone_number": "WRONG",
            "contract_requested": "z",
        }
        access_token = new_client.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client.client_id
        response = api_client.put(
            reverse("client_detail", kwargs={"client_id": client_id}),
            headers=headers,
            data=invalid_client_data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Client.objects.count() == 1
        assert (
            "La saisie doit comporter uniquement des caractères alphanumériques, apostrophe, tiret, @, point, espace."
            in response.data["company_name"]
        )
        assert (
            "La saisie doit comporter uniquement des caractères numériques."
            in response.data["siren"]
        )
        assert (
            "La saisie doit comporter uniquement des caractères alphabétiques avec apostrophe, tiret et espace."
            in response.data["first_name"]
            and response.data["last_name"]
        )
        assert "Saisissez une adresse e-mail valide." in response.data["email"]
        assert "Le numéro saisi n'est pas valide." in response.data["phone_number"]
        assert "Must be a valid boolean." in response.data["contract_requested"]

    def test_put_client_route_failed_with_forbidden(
        self, api_client, new_client, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for client, a valid unassigned sales_contact token, and valid data
        WHEN the client endpoint is updated to (PUT)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client.client_id
        response = api_client.put(
            reverse("client_detail", kwargs={"client_id": client_id}),
            headers=headers,
            data=self.valid_client_data,
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Client.objects.count() == 1
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_put_client_failed_with_unauthorized(self, api_client, new_client):
        """
        GIVEN a fixture for client, an invalid token, and valid data
        WHEN the client endpoint is updated to (PUT)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client.client_id
        response = api_client.put(
            reverse("employee_detail", kwargs={"employee_id": client_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Client.objects.count() == 1
        assert "token_not_valid" in response.data["code"]

    def test_put_client_sales_contact_route_success(
        self, api_client, new_client, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for client, management employee with valid token, and sales employee id data
        WHEN the client endpoint is updated to (PUT)
        THEN checks that response is 200 and datas are displayed
        """
        updated_sales_contact = new_client.sales_contact
        updated_sales_contact_id = updated_sales_contact.employee_id
        valid_client_data = {"updated_sales_contact": updated_sales_contact_id}
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client.client_id
        response = api_client.put(
            reverse("client_detail", kwargs={"client_id": client_id}),
            headers=headers,
            data=valid_client_data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert Client.objects.count() == 1
        assert str(updated_sales_contact) in response.data["sales_contact"]

    def test_put_client_sales_contact_route_failed_with_no_sales_contact_id_bad_request(
        self, api_client, new_client, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for client, management employee with valid token, and not sales employee id data
        WHEN the client endpoint is updated to (PUT)
        THEN checks that response is 400 and error message is displayed
        """
        management_employee_id = employees_users_with_tokens[
            "management_employee"
        ].employee_id
        invalid_client_data = {"updated_sales_contact": management_employee_id}
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client.client_id
        response = api_client.put(
            reverse("client_detail", kwargs={"client_id": client_id}),
            headers=headers,
            data=invalid_client_data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Client.objects.count() == 1
        assert (
            "Le sales_contact doit être un employé du département ventes."
            in response.data["details"]
        )

    def test_put_client_sales_contact_route_failed_with_invalid_id_bad_request(
        self, api_client, new_client, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for client, management employee with valid token, and invalid uuid data
        WHEN the client endpoint is updated to (PUT)
        THEN checks that response is 400 and error message is displayed
        """
        invalid_client_data = {
            "updated_sales_contact": "f37790ce-a3c1-474b-9e8a-b7a959a80b8e"
        }
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client.client_id
        response = api_client.put(
            reverse("client_detail", kwargs={"client_id": client_id}),
            headers=headers,
            data=invalid_client_data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Client.objects.count() == 1
        assert (
            "Il n'existe pas d'employé correspondant à cet identifiant."
            in response.data["details"]
        )


class TestDeleteClient:
    """
    GIVEN fixtures for client with location, employees with their associated users and tokens and contract
    WHEN user tries to delete a client via id
    THEN checks that the response is valid
    """

    def test_delete_client_route_success(self, api_client, new_client_with_location):
        """
        GIVEN a fixture for client with its sales_contact valid token and location
        WHEN the client endpoint is deleted (DEL)
        THEN checks that response is 204
        """
        access_token = new_client_with_location.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client_with_location.client_id
        response = api_client.delete(
            reverse("client_detail", kwargs={"client_id": client_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Client.objects.count() == 0
        assert Location.objects.count() == 0

    def test_delete_client_route_failed_with_forbidden(
        self, api_client, new_client, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for client and a valid unassigned sales contact
        WHEN the client endpoint is deleted (DEL)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client.client_id
        response = api_client.delete(
            reverse("client_detail", kwargs={"client_id": client_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Client.objects.count() == 1
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_delete_client_route_failed_with_unauthorized(self, api_client, new_client):
        """
        GIVEN a fixture for client and an invalid token
        WHEN the client endpoint is deleted (DEL)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client.client_id
        response = api_client.delete(
            reverse("employee_detail", kwargs={"employee_id": client_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Client.objects.count() == 1
        assert "token_not_valid" in response.data["code"]

    def test_delete_client_route_with_signed_contract_unauthorized(
        self, api_client, new_contract
    ):
        """
        GIVEN a fixture for contract with client and its sales contact valid token
        WHEN the client with is_signed contract endpoint is deleted (DEL)
        THEN checks that response is 400 and error message is displayed
        """
        new_contract.is_signed = True
        new_contract.save()
        access_token = new_contract.client.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_contract.client.client_id
        response = api_client.delete(
            reverse("client_detail", kwargs={"client_id": client_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Client.objects.count() == 1
        assert (
            "Vous ne pouvez pas supprimer un client dont au moins un contrat est signé."
            in response.data["details"]
        )
