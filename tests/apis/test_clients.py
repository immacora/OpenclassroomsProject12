from rest_framework import status
from django.urls import reverse

from clients.models import Client
from tests.factories import ClientFactory


class TestGetClients:
    """
    GIVEN fixtures for clients and employees with their associated users and tokens
    WHEN user tries to get clients
    THEN checks that the response is valid and data are displayed
    """

    def test_get_clients_route_success_with_manager_employee(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for clients and management employee with valid token
        WHEN the clients endpoint is requested (GET)
        THEN checks that response is 200 and datas are displayed
        """
        clients = ClientFactory.create_batch(5)  # noqa: F841
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.get(reverse("clients"), headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert Client.objects.count() == 5
        assert 5 == response.data["count"]
        assert len(response.data["results"]) == 5

    def test_get_clients_route_success_with_sales_employee(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for clients and sales employee with valid token
        WHEN the clients endpoint is requested (GET)
        THEN checks that response is 200 and datas are displayed
        """
        clients = ClientFactory.create_batch(5)  # noqa: F841
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.get(reverse("clients"), headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert Client.objects.count() == 5
        assert 5 == response.data["count"]
        assert len(response.data["results"]) == 5

    def test_get_clients_route_success_with_support_employee(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for clients and support employee with valid token
        WHEN the clients endpoint is requested (GET)
        THEN checks that response is 200 and datas are displayed
        """
        clients = ClientFactory.create_batch(5)  # noqa: F841
        access_token = employees_users_with_tokens["support_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.get(reverse("clients"), headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert Client.objects.count() == 5
        assert 5 == response.data["count"]
        assert len(response.data["results"]) == 5

    def test_get_clients_route_failed_with_unauthorized(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for clients and invalid token
        WHEN the clients endpoint is requested (GET)
        THEN checks that response is 401 and error message is displayed
        """
        clients = ClientFactory.create_batch(5)  # noqa: F841
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.get(reverse("clients"), headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Client.objects.count() == 5
        assert "token_not_valid" in response.data["code"]


class TestPostClients:
    """
    GIVEN a fixture for employees with their associated users and tokens, valid and invalid client data
    WHEN user tries to create a new client
    THEN checks that the response is valid and data are displayed
    """

    valid_client_data = {
        "company_name": "TEST CREATE Entreprise",
        "siren": "452268192",
        "first_name": "TEST CREATE Prénom du client",
        "last_name": "TEST CREATE Nom du client",
        "email": "TESTCREATEclient@email.com",
        "phone_number": "+33600000000",
    }
    invalid_client_data = {
        "company_name": "<",
        "siren": "a",
        "first_name": "1",
        "last_name": "@",
        "email": "WRONG",
        "phone_number": "WRONG",
    }

    def test_post_clients_route_success(self, api_client, employees_users_with_tokens):
        """
        GIVEN a fixture for sales employee with valid token and valid data
        WHEN the clients endpoint is posted to (POST)
        THEN checks that response is 200 and datas are displayed
        """
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse("clients"),
            headers=headers,
            data=self.valid_client_data,
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Client.objects.count() == 1
        assert "client_id" in response.data
        assert "TEST CREATE Entreprise" in response.data["company_name"]
        assert 452268192 == int(response.data["siren"])
        assert "TEST CREATE Prénom du client" in response.data["first_name"]
        assert "TEST CREATE Nom du client" in response.data["last_name"]
        assert "TESTCREATEclient@email.com" in response.data["email"]
        assert "+33600000000" in response.data["phone_number"]
        assert response.data["contract_requested"] is False

    def test_post_clients_route_failed_with_bad_request(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a fixture for sales employee with valid token and invalid data
        WHEN the clients endpoint is posted to (POST)
        THEN checks that response is 400 and error messages are displayed
        """
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse("clients"),
            headers=headers,
            data=self.invalid_client_data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Client.objects.count() == 0
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

    def test_post_clients_route_failed_with_forbidden(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a fixture for support employee with valid token and valid data
        WHEN the clients endpoint is posted to (POST)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["support_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse("clients"),
            headers=headers,
            data=self.valid_client_data,
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Client.objects.count() == 0
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_post_clients_failed_with_unauthorized(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN an invalid token and valid data
        WHEN the clients endpoint is posted to (POST)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse("clients"),
            headers=headers,
            data=self.valid_client_data,
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Client.objects.count() == 0
        assert "token_not_valid" in response.data["code"]
