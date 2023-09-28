import uuid
from datetime import datetime
from rest_framework import status
from django.db import transaction
from django.urls import reverse

from events.models import Event


class TestPostClientContractEvent:
    """
    GIVEN fixtures for contract, event and employees with their associated users and tokens,
    valid and invalid event data
    WHEN user tries to create a new event
    THEN checks that the response is valid and data are displayed
    """

    valid_data = {
        "event_name": "Event TEST du contrat 1 du client 1",
        "start_date": "2023-12-15T12:00:00+01:00",
        "end_date": "2023-12-15T18:00:00+01:00",
        "attendees": 28,
        "notes": "Notes sur l'événement TEST du contrat n°1 pour le client 1.",
    }
    invalid_data = {
        "event_name": "/Event TEST du contrat 1 du client 1",
        "end_date": "1",
        "attendees": "",
        "notes": "<Notes sur l'événement TEST du contrat n°1 pour le client 1.",
    }

    def test_post_client_contract_event_route_success(self, api_client, new_contract):
        """
        GIVEN a fixture for contract with its client sales_contact valid token and valid data
        WHEN the event endpoint is posted to (POST)
        THEN checks that response is 201 and datas are displayed
        """
        new_contract.is_signed = True
        new_contract.save()
        access_token = new_contract.client.sales_contact.user.access_token
        client_id = new_contract.client.client_id
        contract_id = new_contract.contract_id
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse(
                "client_contract_event",
                kwargs={"client_id": client_id, "contract_id": contract_id},
            ),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Event.objects.count() == 1
        assert "event_id" in response.data
        assert "Event TEST du contrat 1 du client 1" in response.data["event_name"]
        assert "2023-12-15T12:00:00+01:00" in response.data["start_date"]
        assert "2023-12-15T18:00:00+01:00" in response.data["end_date"]
        assert 28 == int(response.data["attendees"])
        assert (
            "Notes sur l'événement TEST du contrat n°1 pour le client 1."
            in response.data["notes"]
        )
        assert response.data["support_contact"] is None

    def test_post_client_contract_event_route_failed_with_bad_request(
        self, api_client, new_contract
    ):
        """
        GIVEN a fixture for contract with its client sales_contact valid token and invalid data
        WHEN the event endpoint is posted to (POST)
        THEN checks that response is 400 and error messages are displayed
        """
        new_contract.is_signed = True
        new_contract.save()
        access_token = new_contract.client.sales_contact.user.access_token
        client_id = new_contract.client.client_id
        contract_id = new_contract.contract_id
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse(
                "client_contract_event",
                kwargs={"client_id": client_id, "contract_id": contract_id},
            ),
            headers=headers,
            data=self.invalid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Event.objects.count() == 0
        assert (
            "La saisie doit comporter uniquement des caractères alphanumériques, apostrophe, tiret, @, point, espace."
            in response.data["event_name"]
        )
        assert "Ce champ est obligatoire." in response.data["start_date"]
        assert (
            "La date + heure n'a pas le bon format. Utilisez un des formats suivants\xa0: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."  # noqa: E501, W505
            in response.data["end_date"]
        )
        assert "Un nombre entier valide est requis." in response.data["attendees"]
        assert (
            "La saisie ne doit pas comporter de caractères spéciaux."
            in response.data["notes"]
        )

    def test_post_client_contract_event_route_failed_with_not_signed_contract_bad_request(
        self, api_client, new_contract
    ):
        """
        GIVEN a fixture for contract with its client sales_contact valid token and valid data
        WHEN the event endpoint is posted to (POST) and contract is not signed
        THEN checks that response is 201 and datas are displayed
        """
        access_token = new_contract.client.sales_contact.user.access_token
        client_id = new_contract.client.client_id
        contract_id = new_contract.contract_id
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse(
                "client_contract_event",
                kwargs={"client_id": client_id, "contract_id": contract_id},
            ),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Event.objects.count() == 0
        assert (
            "Le contrat doit être signé pour créer un événement."
            in response.data["details"]
        )

    def test_post_client_contract_event_route_failed_with_event_exists_bad_request(
        self, api_client, new_contract, new_event
    ):
        """
        GIVEN fixtures for contract with its client sales_contact valid token, event, and valid data
        WHEN the event endpoint is posted to (POST) for the same contract
        THEN checks that response is 400 and error messages is displayed
        """
        new_contract.is_signed = True
        new_contract.save()
        new_event.contract = new_contract
        new_event.save()
        access_token = new_contract.client.sales_contact.user.access_token
        client_id = new_contract.client.client_id
        contract_id = new_contract.contract_id
        headers = {"Authorization": f"Bearer {access_token}"}
        with transaction.atomic():
            response = api_client.post(
                reverse(
                    "client_contract_event",
                    kwargs={"client_id": client_id, "contract_id": contract_id},
                ),
                headers=headers,
                data=self.valid_data,
                format="json",
            )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Event.objects.count() == 1
        assert "Un événement existe déjà pour ce contrat." in response.data["details"]

    def test_post_client_contract_event_route_failed_with_forbidden(
        self, api_client, new_contract, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for contract, valid unassigned sales contact token and valid data
        WHEN the event endpoint is posted to (POST)
        THEN checks that response is 403 and error message is displayed
        """
        new_contract.is_signed = True
        new_contract.save()
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        client_id = new_contract.client.client_id
        contract_id = new_contract.contract_id
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse(
                "client_contract_event",
                kwargs={"client_id": client_id, "contract_id": contract_id},
            ),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Event.objects.count() == 0
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_post_client_contract_event_failed_with_unauthorized(
        self, api_client, new_contract
    ):
        """
        GIVEN a fixture for contract, an invalid token and valid data
        WHEN the event endpoint is posted to (POST)
        THEN checks that response is 401 and error message is displayed
        """
        new_contract.is_signed = True
        new_contract.save()
        access_token = "INVALIDTOKEN"
        client_id = new_contract.client.client_id
        contract_id = new_contract.contract_id
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse(
                "client_contract_event",
                kwargs={"client_id": client_id, "contract_id": contract_id},
            ),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Event.objects.count() == 0
        assert "token_not_valid" in response.data["code"]


class TestGetClientContractEvent:
    """
    GIVEN fixtures for event and employees with their associated users and tokens
    WHEN user tries to get client contract event via id
    THEN checks that the response is valid and data are displayed
    """

    def test_get_client_contract_event_route_success(self, api_client, new_event):
        """
        GIVEN a fixture for event with its support_contact valid token
        WHEN the client_contract_event_detail endpoint is requested (GET)
        THEN checks that response is 200 and datas are displayed
        """
        access_token = new_event.support_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event.contract.client.client_id
        contract_id = new_event.contract.contract_id
        event_id = new_event.event_id
        response = api_client.get(
            reverse(
                "client_contract_event_detail",
                kwargs={
                    "client_id": client_id,
                    "contract_id": contract_id,
                    "event_id": event_id,
                },
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        response_start_date = datetime.fromisoformat(response.data["start_date"])
        response_end_date = datetime.fromisoformat(response.data["end_date"])
        assert new_event.start_date == response_start_date
        assert Event.objects.count() == 1
        assert event_id == uuid.UUID(response.data["event_id"])
        assert new_event.event_name in response.data["event_name"]
        assert new_event.start_date == response_start_date
        assert new_event.end_date == response_end_date
        assert new_event.attendees == int(response.data["attendees"])
        assert new_event.notes in response.data["notes"]
        assert "created_at" in response.data
        assert "updated_at" in response.data
        assert contract_id == uuid.UUID(response.data["contract"]["contract_id"])
        assert client_id == uuid.UUID(response.data["contract"]["client"]["client_id"])

    def test_get_client_contract_event_route_failed_with_forbidden(
        self, api_client, new_event, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for event and valid unassigned support_contact token
        WHEN the client_contract_event_detail endpoint is requested (GET)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["support_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event.contract.client.client_id
        contract_id = new_event.contract.contract_id
        event_id = new_event.event_id
        response = api_client.get(
            reverse(
                "client_contract_event_detail",
                kwargs={
                    "client_id": client_id,
                    "contract_id": contract_id,
                    "event_id": event_id,
                },
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Event.objects.count() == 1
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_get_client_contract_event_route_failed_with_unauthorized(
        self, api_client, new_event
    ):
        """
        GIVEN a fixture for event and an invalid token
        WHEN the client_contract_event_detail endpoint is requested (GET)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event.contract.client.client_id
        contract_id = new_event.contract.contract_id
        event_id = new_event.event_id
        response = api_client.get(
            reverse(
                "client_contract_event_detail",
                kwargs={
                    "client_id": client_id,
                    "contract_id": contract_id,
                    "event_id": event_id,
                },
            ),
            headers=headers,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Event.objects.count() == 1
        assert "token_not_valid" in response.data["code"]

    def test_get_client_contract_event_route_failed_with_not_found(
        self, api_client, new_event
    ):
        """
        GIVEN a fixture for event with its support_contact valid token
        WHEN the client_contract_event_detail endpoint is requested (GET)
        THEN checks that response is 404
        """
        access_token = new_event.support_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event.contract.client.client_id
        contract_id = new_event.contract.contract_id
        response = api_client.get(
            f"api/clients/{client_id}/contracts/{contract_id}/INVALID_event_id/",
            headers=headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Event.objects.count() == 1


class TestPutClientContractEvent:
    """
    GIVEN fixtures for event and employees with their associated users and tokens, valid and invalid event data
    WHEN user tries to update contract event via id
    THEN checks that the response is valid and data are displayed
    """

    valid_data = {
        "event_name": "UPDATED Event 1 du contrat 1 du client TEST",
        "start_date": "2024-11-10T12:00:00+01:00",
        "end_date": "2024-11-10T18:00:00+01:00",
        "attendees": 5,
        "notes": "UPDATED Notes sur l'événement n°1 du contrat n°1 pour le client TEST.",
    }
    invalid_data = {
        "event_name": "/UPDATED Event 1 du contrat 1 du client TEST",
        "start_date": "WRONG",
        "end_date": "WRONG",
        "attendees": "WRONG",
        "notes": "<",
    }

    def test_put_client_contract_event_route_success(self, api_client, new_event):
        """
        GIVEN a fixture for event with its support_contact valid token and valid data
        WHEN the client_contract_event_detail endpoint is updated to (PUT)
        THEN checks that response is 200 and datas are displayed
        """
        access_token = new_event.support_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event.contract.client.client_id
        contract_id = new_event.contract.contract_id
        event_id = new_event.event_id
        response = api_client.put(
            reverse(
                "client_contract_event_detail",
                kwargs={
                    "client_id": client_id,
                    "contract_id": contract_id,
                    "event_id": event_id,
                },
            ),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert Event.objects.count() == 1
        assert event_id == uuid.UUID(response.data["event_id"])
        assert (
            "UPDATED Event 1 du contrat 1 du client TEST" in response.data["event_name"]
        )
        assert "2024-11-10T12:00:00+01:00" in response.data["start_date"]
        assert "2024-11-10T18:00:00+01:00" in response.data["end_date"]
        assert 5 == int(response.data["attendees"])
        assert (
            "UPDATED Notes sur l'événement n°1 du contrat n°1 pour le client TEST."
            in response.data["notes"]
        )
        assert response.data["support_contact"] is not None
        assert new_event.is_event_over is False
        assert response.data["created_at"] != response.data["updated_at"]

    def test_put_client_contract_route_failed_with_bad_request(
        self, api_client, new_event
    ):
        """
        GIVEN a fixture for event with its support_contact valid token and invalid data
        WHEN the client_contract_event_detail endpoint is updated to (PUT)
        THEN checks that response is 200 and datas are displayed
        """
        access_token = new_event.support_contact.user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event.contract.client.client_id
        contract_id = new_event.contract.contract_id
        event_id = new_event.event_id
        response = api_client.put(
            reverse(
                "client_contract_event_detail",
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
        assert Event.objects.count() == 1
        assert (
            "La saisie doit comporter uniquement des caractères alphanumériques, apostrophe, tiret, @, point, espace."
            in response.data["event_name"]
        )
        assert (
            "La date + heure n'a pas le bon format. Utilisez un des formats suivants\xa0: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."  # noqa: E501, W505
            in response.data["start_date"]
        )
        assert (
            "La date + heure n'a pas le bon format. Utilisez un des formats suivants\xa0: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."  # noqa: E501, W505
            in response.data["end_date"]
        )
        assert "Un nombre entier valide est requis." in response.data["attendees"]
        assert (
            "La saisie ne doit pas comporter de caractères spéciaux."
            in response.data["notes"]
        )

    def test_put_client_contract_event_update_support_contact_route_success(
        self, api_client, new_event, new_support_contact, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for event, new_support_contact, valid management employee token and valid data
        WHEN the client_contract_event_detail endpoint is updated to (PUT) with updated_support_contact
        THEN checks that response is 200 and datas are displayed
        """
        new_support_contact_id = new_support_contact.employee_id
        valid_data = {"updated_support_contact": new_support_contact_id}
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event.contract.client.client_id
        contract_id = new_event.contract.contract_id
        event_id = new_event.event_id
        response = api_client.put(
            reverse(
                "client_contract_event_detail",
                kwargs={
                    "client_id": client_id,
                    "contract_id": contract_id,
                    "event_id": event_id,
                },
            ),
            headers=headers,
            data=valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert Event.objects.count() == 1
        assert event_id == uuid.UUID(response.data["event_id"])
        assert (
            str(new_support_contact)
            in response.data["support_contact"]["representation_str"]
        )

    def test_put_client_contract_event_route_failed_with_not_support_employee_bad_request(
        self, api_client, new_event, new_sales_contact, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for event, new_sales_contact, valid management employee token and valid data
        WHEN the client_contract_event_detail endpoint is updated to (PUT) with updated_support_contact
        THEN checks that response is 400 and error message is displayed
        """
        new_sales_contact_id = new_sales_contact.employee_id
        valid_data = {"updated_support_contact": new_sales_contact_id}
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event.contract.client.client_id
        contract_id = new_event.contract.contract_id
        event_id = new_event.event_id
        response = api_client.put(
            reverse(
                "client_contract_event_detail",
                kwargs={
                    "client_id": client_id,
                    "contract_id": contract_id,
                    "event_id": event_id,
                },
            ),
            headers=headers,
            data=valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Event.objects.count() == 1
        assert (
            "Le support_contact doit être un employé du département support."
            in response.data["details"]
        )

    def test_put_client_contract_event_route_failed_with_forbidden(
        self, api_client, new_event, employees_users_with_tokens
    ):
        """
        GIVEN fixtures for event, valid unassigned support_contact token and valid data
        WHEN the client_contract_event_detail endpoint is updated to (PUT)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["support_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event.contract.client.client_id
        contract_id = new_event.contract.contract_id
        event_id = new_event.event_id
        response = api_client.put(
            reverse(
                "client_contract_event_detail",
                kwargs={
                    "client_id": client_id,
                    "contract_id": contract_id,
                    "event_id": event_id,
                },
            ),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Event.objects.count() == 1
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_put_client_contract_event_failed_with_unauthorized(
        self, api_client, new_event
    ):
        """
        GIVEN fixtures for event, an invalid token and valid data
        WHEN the client_contract_event_detail endpoint is updated to (PUT)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        client_id = new_event.contract.client.client_id
        contract_id = new_event.contract.contract_id
        event_id = new_event.event_id
        response = api_client.put(
            reverse(
                "client_contract_event_detail",
                kwargs={
                    "client_id": client_id,
                    "contract_id": contract_id,
                    "event_id": event_id,
                },
            ),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Event.objects.count() == 1
        assert "token_not_valid" in response.data["code"]
