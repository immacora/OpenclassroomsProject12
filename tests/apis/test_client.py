from django.contrib.auth import get_user_model
from rest_framework import status
from django.urls import reverse

from clients.models import Client
from locations.models import Location
from accounts.models import Employee

CustomUser = get_user_model()


class TestGetClient:
    """
    GIVEN fixtures for client (with location and sales contact with tokens) and employees with their associated users and tokens
    WHEN user tries to get client via id
    THEN checks that the response is valid and data are displayed
    """

    def test_get_client_route_success(self, api_client, new_client):
        """
        GIVEN an existing client and his sales contact valid token
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
        assert Location.objects.count() == 1
        assert Employee.objects.count() == 1
        assert CustomUser.objects.count() == 1
        assert str(client_id) in response.data["client_id"]
        assert new_client.company_name == response.data["company_name"]
        assert new_client.siren == response.data["siren"]
        assert new_client.last_name in response.data["last_name"]
        assert new_client.first_name in response.data["first_name"]
        assert new_client.email in response.data["email"]
        assert str(new_client.phone_number) in response.data["phone_number"]
        assert "SALES" in response.data["sales_contact"]
        assert "created_at" in response.data
        assert "updated_at" in response.data

    def test_get_client_route_failed_with_forbidden(
        self, api_client, new_client, employees_users_with_tokens
    ):
        """
        GIVEN an existing client and a valid unassigned sales contact token
        WHEN user tries to get client via id
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
        assert Location.objects.count() == 1
        assert Employee.objects.count() == 4
        assert CustomUser.objects.count() == 4
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )
        assert "client_id" not in response.data

    def test_get_client_route_failed_with_unauthorized(self, api_client, new_client):
        """
        GIVEN an invalid token and an existing client
        WHEN user tries to get client via id
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
        assert Location.objects.count() == 1
        assert Employee.objects.count() == 1
        assert CustomUser.objects.count() == 1
        assert "token_not_valid" in response.data["code"]

    def test_get_client_route_failed_with_not_found(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a sales employee valid token and a invalid client_id
        WHEN the client endpoint is requested (GET)
        THEN checks that response is 404 and error message is displayed
        """
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.delete("api/clients/1234/", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Client.objects.count() == 0
        assert Location.objects.count() == 0
        assert Employee.objects.count() == 3
        assert CustomUser.objects.count() == 3


class TestPutClient:
    """
    GIVEN fixtures for client (with location and sales contact with tokens) and employees with their associated users and tokens
    WHEN user tries to edit a client
    THEN checks that the response is valid and data are displayed
    """

    valid_client_data = {
        "company_name": "UPDATED Entreprise TEST",
        "siren": "111111111",
        "first_name": "UPDATED Prénom du client TEST",
        "last_name": "UPDATED Nom du client TEST",
        "email": "UPDATEDclientTEST@email.com",
        "phone_number": "+33600000000",
        "locations": [
            {
                "street_number": 111,
                "street_name": "Rue du lieu ADD LOCATION",
                "city": "VILLE-DU-LIEU ADD LOCATION",
                "zip_code": "09999",
                "country": "FRANCE ADD LOCATION",
            }
        ],
    }

    def test_put_client_route_success(self, api_client, new_client):
        """
        GIVEN an existing client with a location, his sales contact valid token, and valid data
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
        assert Location.objects.count() == 2
        assert Employee.objects.count() == 1
        assert CustomUser.objects.count() == 1
        assert str(client_id) in response.data["client_id"]
        assert "UPDATED Entreprise TEST" in response.data["company_name"]
        assert 111111111 == int(response.data["siren"])
        assert "UPDATED Prénom du client TEST" in response.data["first_name"]
        assert "UPDATED Nom du client TEST" in response.data["last_name"]
        assert "UPDATEDclientTEST@email.com" in response.data["email"]
        assert "+33600000000" == response.data["phone_number"]
        assert new_client.sales_contact.last_name in response.data["sales_contact"]
        assert response.data["created_at"] != response.data["updated_at"]

    def test_put_client_route_failed_with_client_bad_request(
        self, api_client, new_client
    ):
        """
        GIVEN an existing client with a location, his sales contact valid token, and invalid client data
        WHEN the client endpoint is updated to (PUT)
        THEN checks that response is 400 and error message is displayed
        """
        invalid_client_data = {
            "company_name": "/Entreprise TEST",
            "siren": "WRONG",
            "first_name": ",Prénom du client TEST",
            "last_name": "!Nom du client TEST",
            "email": "WRONG",
            "phone_number": "WRONG",
            "locations": [
                {
                    "street_number": "WRONG",
                    "street_name": "<Rue du lieu 1",
                    "city": ";VILLE-DU-LIEU",
                    "zip_code": "WRONG",
                    "country": "123",
                }
            ],
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
        assert Location.objects.count() == 1
        assert Employee.objects.count() == 1
        assert CustomUser.objects.count() == 1
        assert (
            "La saisie doit comporter uniquement des caractères alphanumériques avec apostrophe, tiret, @, point et espace."
            in response.data["company_name"]
            and response.data["locations"][0]["street_name"]
        )
        assert (
            "La saisie doit comporter uniquement des caractères numériques."
            in response.data["siren"]
            and response.data["locations"][0]["zip_code"]
        )
        assert (
            "La saisie doit comporter uniquement des caractères alphabétiques avec apostrophe, tiret et espace."
            in response.data["first_name"]
            and response.data["last_name"]
            and response.data["locations"][0]["city"]
            and response.data["locations"][0]["country"]
        )
        assert "Saisissez une adresse e-mail valide." in response.data["email"]
        assert "Le numéro saisi n'est pas valide." in response.data["phone_number"]
        assert (
            "Un nombre entier valide est requis."
            in response.data["locations"][0]["street_number"]
        )

    def test_put_client_route_failed_with_sales_contact_bad_request(
        self, api_client, new_client
    ):
        """
        GIVEN an existing client, his sales contact valid token, and sales_contact in data to update
        WHEN the client endpoint is updated to (PUT)
        THEN checks that response is 400 and error message is displayed
        """
        invalid_data_with_sales_contact = {
            "sales_contact": "1a99f054-8e33-4719-8ab3-d2249a3051dd",
        }
        access_token = new_client.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client.client_id
        response = api_client.put(
            reverse("client_detail", kwargs={"client_id": client_id}),
            headers=headers,
            data=invalid_data_with_sales_contact,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Client.objects.count() == 1
        assert Location.objects.count() == 1
        assert Employee.objects.count() == 1
        assert CustomUser.objects.count() == 1
        assert (
            "Vous ne pouvez pas modifier le commercial attribué."
            in response.data["details"]
        )

    def test_put_client_route_failed_with_forbidden(
        self, api_client, new_client, employees_users_with_tokens
    ):
        """
        GIVEN an existing client with a location, a valid unassigned sales contact token, and valid data
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
        assert Location.objects.count() == 1
        assert Employee.objects.count() == 4
        assert CustomUser.objects.count() == 4
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )
        assert "client_id" not in response.data

    def test_put_client_failed_with_unauthorized(self, api_client, new_client):
        """
        GIVEN an existing client with a location, an invalid token, and valid data
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
        assert Location.objects.count() == 1
        assert Employee.objects.count() == 1
        assert CustomUser.objects.count() == 1
        assert "token_not_valid" in response.data["code"]


class TestDeleteClient:
    """
    GIVEN fixtures for client (with location and sales contact with tokens) and employees with their associated users and tokens
    WHEN user tries to delete a client via id
    THEN checks that the response is valid
    """

    def test_delete_client_route_success(self, api_client, new_client):
        """
        GIVEN an existing client and his sales contact valid token
        WHEN the client endpoint is deleted (DEL)
        THEN checks that response is 204
        """
        access_token = new_client.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client.client_id
        response = api_client.delete(
            reverse("client_detail", kwargs={"client_id": client_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Client.objects.count() == 0
        assert Location.objects.count() == 0
        assert Employee.objects.count() == 1
        assert CustomUser.objects.count() == 1

    def test_delete_client_route_failed_with_forbidden(
        self, api_client, new_client, employees_users_with_tokens
    ):
        """
        GIVEN an existing client and a valid unassigned sales contact
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
        assert Location.objects.count() == 1
        assert Employee.objects.count() == 4
        assert CustomUser.objects.count() == 4
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_delete_client_route_failed_with_unauthorized(self, api_client, new_client):
        """
        GIVEN an existing client and an invalid token
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
        assert Location.objects.count() == 1
        assert Employee.objects.count() == 1
        assert CustomUser.objects.count() == 1
        assert "token_not_valid" in response.data["code"]
