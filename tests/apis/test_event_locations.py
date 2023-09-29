import uuid
from rest_framework import status
from django.urls import reverse

from locations.models import Location


class TestGetEventLocations:
    """
    GIVEN fixtures for event with location and employees with their associated users and tokens
    WHEN user tries to get event locations
    THEN checks that the response is valid and data are displayed
    """

    def test_get_event_locations_route_success(
        self, api_client, new_event_with_location
    ):
        """
        GIVEN a fixture for event with location and its support_contact valid token
        WHEN the client_contract_event_locations endpoint is requested (GET)
        THEN checks that response is 200 and datas are displayed
        """
        access_token = new_event_with_location.support_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event_with_location.contract.client.client_id
        contract_id = new_event_with_location.contract.contract_id
        event_id = new_event_with_location.event_id
        location = new_event_with_location.locations.first()
        response = api_client.get(
            reverse(
                "client_contract_event_locations",
                kwargs={
                    "client_id": client_id,
                    "contract_id": contract_id,
                    "event_id": event_id,
                },
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert Location.objects.count() == 1
        assert location.location_id == uuid.UUID(
            response.data["results"][0]["location_id"]
        )
        assert location.street_number == int(
            response.data["results"][0]["street_number"]
        )
        assert location.street_name in response.data["results"][0]["street_name"]
        assert location.city in response.data["results"][0]["city"]
        assert location.zip_code in response.data["results"][0]["zip_code"]
        assert location.country in response.data["results"][0]["country"]

    def test_get_event_locations_route_failed_with_forbidden(
        self, api_client, new_event_with_location, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for event with location and a valid unassigned support_contact token
        WHEN the client_contract_event_locations endpoint is requested (GET)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["support_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event_with_location.contract.client.client_id
        contract_id = new_event_with_location.contract.contract_id
        event_id = new_event_with_location.event_id
        response = api_client.get(
            reverse(
                "client_contract_event_locations",
                kwargs={
                    "client_id": client_id,
                    "contract_id": contract_id,
                    "event_id": event_id,
                },
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Location.objects.count() == 1
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_get_event_locations_route_failed_with_unauthorized(
        self, api_client, new_event_with_location
    ):
        """
        GIVEN fixtures for event with location and an invalid token
        WHEN the client_contract_event_locations endpoint is requested (GET)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event_with_location.contract.client.client_id
        contract_id = new_event_with_location.contract.contract_id
        event_id = new_event_with_location.event_id
        response = api_client.get(
            reverse(
                "client_contract_event_locations",
                kwargs={
                    "client_id": client_id,
                    "contract_id": contract_id,
                    "event_id": event_id,
                },
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Location.objects.count() == 1
        assert "token_not_valid" in response.data["code"]


class TestPostEventLocations:
    """
    GIVEN fixtures for event, employees with their associated users and tokens,
    valid and invalid locations data
    WHEN user tries to create location(s) for event
    THEN checks that the response is valid and data are displayed
    """

    location_1 = {
        "street_number": 75,
        "street_name": "Rue du lieu CREE POUR L'EVENT",
        "city": "VILLE-DU-LIEU CREE POUR L EVENT",
        "zip_code": "03000",
        "country": "FRANCE",
    }
    location_2 = {
        "street_number": 8,
        "street_name": "Rue du lieu DEUX CREE POUR L'EVENT",
        "city": "VILLE-DU-LIEU DEUX CREE POUR L EVENT",
        "zip_code": "04000",
        "country": "FRANCE",
    }
    location_valid_data = {"locations": [location_1]}
    locations_valid_data = {"locations": [location_1, location_2]}
    invalid_data = {
        "locations": [
            {
                "street_number": "WRONG",
                "street_name": "/",
                "zip_code": "WRONG",
                "country": "<",
            }
        ]
    }

    def test_post_event_locations_route_with_one_new_location_success(
        self, api_client, new_event
    ):
        """
        GIVEN a fixture for event and its support_contact valid token, and valid location data
        WHEN the client_contract_event_locations endpoint is posted to (POST)
        THEN checks that response is 201 and datas are displayed
        """
        access_token = new_event.support_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event.contract.client.client_id
        contract_id = new_event.contract.contract_id
        event_id = new_event.event_id
        response = api_client.post(
            reverse(
                "client_contract_event_locations",
                kwargs={
                    "client_id": client_id,
                    "contract_id": contract_id,
                    "event_id": event_id,
                },
            ),
            headers=headers,
            data=self.location_valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Location.objects.count() == 1
        assert "location_id" in response.data[0]
        assert 75 == response.data[0]["street_number"]
        assert "Rue du lieu CREE POUR L'EVENT" in response.data[0]["street_name"]
        assert "VILLE-DU-LIEU CREE POUR L EVENT" in response.data[0]["city"]
        assert "03000" in response.data[0]["zip_code"]
        assert "FRANCE" in response.data[0]["country"]

    def test_post_event_locations_route_with_two_new_locations_success(
        self, api_client, new_event
    ):
        """
        GIVEN a fixture for event and its support_contact valid token, and valid location data
        WHEN the client_contract_event_locations endpoint is posted to (POST)
        THEN checks that response is 201 and datas are displayed
        """
        access_token = new_event.support_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event.contract.client.client_id
        contract_id = new_event.contract.contract_id
        event_id = new_event.event_id
        response = api_client.post(
            reverse(
                "client_contract_event_locations",
                kwargs={
                    "client_id": client_id,
                    "contract_id": contract_id,
                    "event_id": event_id,
                },
            ),
            headers=headers,
            data=self.locations_valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Location.objects.count() == 2
        assert "location_id" in response.data[0]
        assert 75 == response.data[0]["street_number"]
        assert "Rue du lieu CREE POUR L'EVENT" in response.data[0]["street_name"]
        assert "VILLE-DU-LIEU CREE POUR L EVENT" in response.data[0]["city"]
        assert "03000" in response.data[0]["zip_code"]
        assert "FRANCE" in response.data[0]["country"]
        assert "location_id" in response.data[1]
        assert 8 == response.data[1]["street_number"]
        assert "Rue du lieu DEUX CREE POUR L'EVENT" in response.data[1]["street_name"]
        assert "VILLE-DU-LIEU DEUX CREE POUR L EVENT" in response.data[1]["city"]
        assert "04000" in response.data[1]["zip_code"]
        assert "FRANCE" in response.data[1]["country"]

    def test_post_event_locations_route_with_existing_location_success(
        self, api_client, new_event, new_location
    ):
        """
        GIVEN fixtures for event and its support_contact valid token, and existing location data
        WHEN the client_contract_event_locations endpoint is posted to (POST)
        THEN checks that response is 201 and datas are displayed
        """
        existing_location_data = {
            "locations": [
                {
                    "street_number": new_location.street_number,
                    "street_name": new_location.street_name,
                    "city": new_location.city,
                    "zip_code": new_location.zip_code,
                    "country": new_location.country,
                }
            ]
        }
        access_token = new_event.support_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event.contract.client.client_id
        contract_id = new_event.contract.contract_id
        event_id = new_event.event_id
        response = api_client.post(
            reverse(
                "client_contract_event_locations",
                kwargs={
                    "client_id": client_id,
                    "contract_id": contract_id,
                    "event_id": event_id,
                },
            ),
            headers=headers,
            data=existing_location_data,
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Location.objects.count() == 1
        assert new_location.location_id == uuid.UUID(response.data[0]["location_id"])

    def test_post_event_locations_route_failed_with_bad_request(
        self, api_client, new_event
    ):
        """
        GIVEN a fixture for event and its support_contact valid token with invalid location data
        WHEN the client_contract_event_locations endpoint is posted to (POST)
        THEN checks that response is 400 and error messages are displayed
        """
        access_token = new_event.support_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event.contract.client.client_id
        contract_id = new_event.contract.contract_id
        event_id = new_event.event_id
        response = api_client.post(
            reverse(
                "client_contract_event_locations",
                kwargs={
                    "client_id": client_id,
                    "contract_id": contract_id,
                    "event_id": event_id,
                },
            ),
            headers=headers,
            data=self.invalid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Location.objects.count() == 0
        assert "Un nombre entier valide est requis." in response.data["street_number"]
        assert (
            "La saisie doit comporter uniquement des caractères alphanumériques, apostrophe, tiret, @, point, espace."
            in response.data["street_name"]
        )
        assert "Ce champ est obligatoire." in response.data["city"]
        assert (
            "La saisie doit comporter uniquement des caractères numériques."
            in response.data["zip_code"]
        )
        assert (
            "La saisie doit comporter uniquement des caractères alphabétiques avec apostrophe, tiret et espace."
            in response.data["country"]
        )

    def test_post_event_locations_route_failed_with_forbidden(
        self, api_client, new_event, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for event and unassigned support_contact valid token with valid location data
        WHEN the client_contract_event_locations endpoint is posted to (POST)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["support_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event.contract.client.client_id
        contract_id = new_event.contract.contract_id
        event_id = new_event.event_id
        response = api_client.post(
            reverse(
                "client_contract_event_locations",
                kwargs={
                    "client_id": client_id,
                    "contract_id": contract_id,
                    "event_id": event_id,
                },
            ),
            headers=headers,
            data=self.location_valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Location.objects.count() == 0
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_post_event_locations_route_failed_with_unauthorized(
        self, api_client, new_event
    ):
        """
        GIVEN a fixture for event, an invalid token and valid data
        WHEN the client_contract_event_locations endpoint is posted to (POST)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event.contract.client.client_id
        contract_id = new_event.contract.contract_id
        event_id = new_event.event_id
        response = api_client.post(
            reverse(
                "client_contract_event_locations",
                kwargs={
                    "client_id": client_id,
                    "contract_id": contract_id,
                    "event_id": event_id,
                },
            ),
            headers=headers,
            data=self.location_valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Location.objects.count() == 0
        assert "token_not_valid" in response.data["code"]
