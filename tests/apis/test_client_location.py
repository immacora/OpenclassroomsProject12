import uuid
from rest_framework import status
from django.urls import reverse

from locations.models import Location


class TestGetClientLocation:
    """
    GIVEN fixtures for client with location and employees with their associated users and tokens
    WHEN user tries to get client location via id
    THEN checks that the response is valid and data are displayed
    """

    def test_get_client_location_route_success(
        self, api_client, new_client_with_location
    ):
        """
        GIVEN a fixture for client with location and its sales contact valid token
        WHEN the client_location_detail endpoint is requested (GET)
        THEN checks that response is 200 and datas are displayed
        """
        access_token = new_client_with_location.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client_with_location.client_id
        location = new_client_with_location.locations.first()
        location_id = location.location_id
        response = api_client.get(
            reverse(
                "client_location_detail",
                kwargs={"client_id": client_id, "location_id": location_id},
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert Location.objects.count() == 1
        assert location_id == uuid.UUID(response.data["location_id"])
        assert location.street_number == int(response.data["street_number"])
        assert location.street_name in response.data["street_name"]
        assert location.city in response.data["city"]
        assert location.zip_code in response.data["zip_code"]
        assert location.country in response.data["country"]

    def test_get_client_location_route_failed_with_forbidden(
        self, api_client, new_client_with_location, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for client with location and valid unassigned sales contact token
        WHEN the client_location_detail endpoint is requested (GET)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client_with_location.client_id
        location = new_client_with_location.locations.first()
        location_id = location.location_id
        response = api_client.get(
            reverse(
                "client_location_detail",
                kwargs={"client_id": client_id, "location_id": location_id},
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Location.objects.count() == 1
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_get_client_location_route_failed_with_unauthorized(
        self, api_client, new_client_with_location
    ):
        """
        GIVEN a fixture for client with location and an invalid token
        WHEN the client_location_detail endpoint is requested (GET)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client_with_location.client_id
        location = new_client_with_location.locations.first()
        location_id = location.location_id
        response = api_client.get(
            reverse(
                "client_location_detail",
                kwargs={"client_id": client_id, "location_id": location_id},
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Location.objects.count() == 1
        assert "token_not_valid" in response.data["code"]

    def test_get_client_location_route_failed_with_not_found(
        self, api_client, new_client_with_location
    ):
        """
        GIVEN a fixture for client with location, its sales contact valid token and invalid location_id
        WHEN the client_location_detail endpoint is requested (GET)
        THEN checks that response is 404
        """
        access_token = new_client_with_location.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client_with_location.client_id
        response = api_client.get(
            f"api/clients/{client_id}/locations/INVALID_location_id/", headers=headers
        )
        assert Location.objects.count() == 1
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPutClientLocation:
    """
    GIVEN fixtures for client with location and employees with their associated users and tokens,
    valid and invalid location data
    WHEN user tries to update client location via id
    THEN checks that the response is valid and data are displayed
    """

    valid_data = {
        "street_number": 1234,
        "street_name": "UPDATED Rue du lieu TEST",
        "city": "UPDATED-VILLE-DU-LIEU-TEST",
        "zip_code": "11111",
        "country": "UPDATED",
    }
    invalid_data = {
        "street_number": "WRONG",
        "street_name": "/",
        "city": "1",
        "zip_code": "WRONG",
        "country": ">",
    }

    def test_put_client_location_route_success(
        self, api_client, new_client_with_location
    ):
        """
        GIVEN a fixture for client with location, its sales contact valid token and valid data
        WHEN the client_location_detail endpoint is updated to (PUT)
        THEN checks that response is 200 and datas are displayed
        """
        access_token = new_client_with_location.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client_with_location.client_id
        location_id = new_client_with_location.locations.first().location_id
        response = api_client.put(
            reverse(
                "client_location_detail",
                kwargs={"client_id": client_id, "location_id": location_id},
            ),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert Location.objects.count() == 1
        assert location_id == uuid.UUID(response.data["location_id"])
        assert 1234 == int(response.data["street_number"])
        assert "UPDATED Rue du lieu TEST" in response.data["street_name"]
        assert "UPDATED-VILLE-DU-LIEU-TEST" in response.data["city"]
        assert 11111 == int(response.data["zip_code"])
        assert "UPDATED" in response.data["country"]

    def test_put_client_location_route_failed_with_bad_request(
        self, api_client, new_client_with_location
    ):
        """
        GIVEN a fixture for client with location, its sales contact valid token and invalid data
        WHEN the client_location_detail endpoint is updated to (PUT)
        THEN checks that response is 400 and error messages are displayed
        """
        access_token = new_client_with_location.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client_with_location.client_id
        location = new_client_with_location.locations.first()
        location_id = location.location_id
        response = api_client.put(
            reverse(
                "client_location_detail",
                kwargs={"client_id": client_id, "location_id": location_id},
            ),
            headers=headers,
            data=self.invalid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Location.objects.count() == 1
        assert "Un nombre entier valide est requis." in response.data["street_number"]
        assert (
            "La saisie doit comporter uniquement des caractères alphanumériques, apostrophe, tiret, @, point, espace."
            in response.data["street_name"]
        )
        assert (
            "La saisie doit comporter uniquement des caractères alphabétiques avec apostrophe, tiret et espace."
            in response.data["city"]
        )
        assert (
            "La saisie doit comporter uniquement des caractères numériques."
            in response.data["zip_code"]
        )
        assert (
            "La saisie doit comporter uniquement des caractères alphabétiques avec apostrophe, tiret et espace."
            in response.data["country"]
        )

    def test_put_client_location_route_failed_with_forbidden(
        self, api_client, new_client_with_location, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for client with location, valid unassigned sales_contact token and valid data
        WHEN the client_location_detail endpoint is updated to (PUT)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client_with_location.client_id
        location = new_client_with_location.locations.first()
        location_id = location.location_id
        response = api_client.put(
            reverse(
                "client_location_detail",
                kwargs={"client_id": client_id, "location_id": location_id},
            ),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Location.objects.count() == 1
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_put_client_location_route_failed_with_used_location_forbidden(
        self, api_client, new_client_with_location, new_client, new_location
    ):
        """
        GIVEN fixtures for client with location and client, with sales contacts valids tokens, location, and valid data
        WHEN the client_location_detail endpoint is updated with the location added to both clients (PUT)
        THEN checks that response is 403 and error message is displayed
        """
        new_client_with_location.locations.add(new_location)
        new_client.locations.add(new_location)
        access_token = new_client.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        new_client_client_id = new_client.client_id
        new_client_location_id = new_client.locations.first().location_id
        response = api_client.put(
            reverse(
                "client_location_detail",
                kwargs={
                    "client_id": new_client_client_id,
                    "location_id": new_client_location_id,
                },
            ),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Location.objects.count() == 2
        assert (
            "Ce lieu est utilisé par un autre modèle. Vous devez le supprimer de ce modèle."
            in response.data["details"]
        )

    def test_put_client_location_failed_with_unauthorized(
        self, api_client, new_client_with_location
    ):
        """
        GIVEN a fixture for client, an invalid token and valid data
        WHEN the client_location_detail endpoint is updated to (PUT)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client_with_location.client_id
        location_id = new_client_with_location.locations.first().location_id
        response = api_client.put(
            reverse(
                "client_location_detail",
                kwargs={"client_id": client_id, "location_id": location_id},
            ),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Location.objects.count() == 1
        assert "token_not_valid" in response.data["code"]


class TestDeleteClientLocation:
    """
    GIVEN fixtures for client with location, employees with their associated users and tokens, and location
    WHEN user tries to delete a client via id
    THEN checks that the response is valid or error message is displayed
    """

    def test_delete_client_location_from_app_route_success(
        self, api_client, new_client_with_location
    ):
        """
        GIVEN a fixture for client with location and its sales contact valid token
        WHEN the client_location_detail endpoint is deleted (DEL)
        THEN checks that response is 204
        """
        access_token = new_client_with_location.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client_with_location.client_id
        location_id = new_client_with_location.locations.first().location_id
        response = api_client.delete(
            reverse(
                "client_location_detail",
                kwargs={"client_id": client_id, "location_id": location_id},
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Location.objects.count() == 0

    def test_delete_client_location_from_client_route_success(
        self, api_client, new_client_with_location, new_client, new_location
    ):
        """
       GIVEN fixtures for client with location, client with its sales contact valid token and location
        WHEN the client_location_detail endpoint is deleted (DEL)
        THEN checks that response is 200 and message is displayed
        """
        new_client_with_location.locations.add(new_location)
        new_client.locations.add(new_location)
        access_token = new_client.sales_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        new_client_client_id = new_client.client_id
        new_client_location_id = new_client.locations.first().location_id
        response = api_client.delete(
            reverse(
                "client_location_detail",
                kwargs={
                    "client_id": new_client_client_id,
                    "location_id": new_client_location_id,
                },
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert Location.objects.count() == 2
        assert ("Le lieu a été retiré de ce client." in response.data["details"])

    def test_delete_client_location_route_failed_with_forbidden(
        self, api_client, new_client_with_location, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for client with location and valid unassigned sales contact with token
        WHEN the client_location_detail endpoint is deleted (DEL)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client_with_location.client_id
        location_id = new_client_with_location.locations.first().location_id
        response = api_client.delete(
            reverse(
                "client_location_detail",
                kwargs={"client_id": client_id, "location_id": location_id},
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Location.objects.count() == 1
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_delete_client_location_route_failed_with_unauthorized(
        self, api_client, new_client_with_location
    ):
        """
        GIVEN a fixture for client with location and invalid token
        WHEN the client_location_detail endpoint is deleted (DEL)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_client_with_location.client_id
        location_id = new_client_with_location.locations.first().location_id
        response = api_client.delete(
            reverse(
                "client_location_detail",
                kwargs={"client_id": client_id, "location_id": location_id},
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Location.objects.count() == 1
        assert "token_not_valid" in response.data["code"]
