from django.contrib.auth import get_user_model
from rest_framework import status
from django.urls import reverse

from accounts.models import Employee

CustomUser = get_user_model()


class TestGetEmployees:
    """
    GIVEN fixture for employees with their associated users and tokens
    WHEN user tries to get the list of employees
    THEN checks that the response is valid and data are displayed
    """

    def test_get_employees_route_success(self, api_client, employees_users_with_tokens):
        """
        GIVEN a management employee valid token
        WHEN the employees endpoint is requested (GET)
        THEN checks that response is 200 and datas are displayed
        """
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.get(reverse("employees"), headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert Employee.objects.count() == 3
        assert CustomUser.objects.count() == 3
        assert "count" in response.data
        assert "results" in response.data

    def test_get_employees_route_failed_with_forbidden(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a sales employee valid token
        WHEN the employees endpoint is requested (GET)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["sales_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.get(reverse("employees"), headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Employee.objects.count() == 3
        assert CustomUser.objects.count() == 3
        assert "count" not in response.data
        assert "results" not in response.data
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_get_employees_route_failed_with_unauthorized(self, api_client, employees_users_with_tokens):
        """
        GIVEN an invalid token
        WHEN the employees endpoint is requested (GET)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.get(reverse("employees"), headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Employee.objects.count() == 3
        assert CustomUser.objects.count() == 3
        assert "token_not_valid" in response.data["code"]


class TestPostEmployees:
    """
    GIVEN fixture for employees with their associated users and tokens
    WHEN user tries to create a new employee with his associated user
    THEN checks that the response is valid and data are displayed
    """

    valid_data = {
        "employee_number": "7402",
        "first_name": "Prénom de test",
        "last_name": "Nom de test",
        "department": "MANAGEMENT",
        "user": {
            "email": "testcreateemployee@email.com",
            "password": "123456789!",
            "password2": "123456789!",
        },
    }
    invalid_data = {
        "employee_number": "-6",
        "first_name": "Prénom/ de test",
        "last_name": "",
        "department": "?",
        "user": {"email": "test", "password": "123456789!"},
    }

    def test_post_employees_route_success(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a management employee valid token and valid data
        WHEN the employees endpoint is posted to (POST)
        THEN checks that response is 200 and datas are displayed
        """
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse("employees"), headers=headers, data=self.valid_data, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Employee.objects.count() == 4
        assert CustomUser.objects.count() == 4
        assert "employee_id" in response.data
        assert 7402 == response.data["employee_number"]
        assert "Nom de test" in response.data["last_name"]
        assert "Prénom de test" in response.data["first_name"]
        assert "MANAGEMENT" in response.data["department"]
        assert b"user_id" in response.content
        assert "testcreateemployee@email.com" in response.data["user"]["email"]
        assert b"password" not in response.content
        assert True == response.data["user"]["is_active"]  # noqa: E712
        assert True == response.data["user"]["is_staff"]  # noqa: E712
        assert "date_joined" in response.data["user"]
        assert "created_at" in response.data
        assert "updated_at" in response.data

    def test_post_employees_route_failed_with_bad_request(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a management employee valid token and invalid data
        WHEN the employees endpoint is posted to (POST)
        THEN checks that response is 400 and error message is displayed
        """
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse("employees"), headers=headers, data=self.invalid_data, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Employee.objects.count() == 3
        assert CustomUser.objects.count() == 3
        assert (
            "Assurez-vous que cette valeur est supérieure ou égale à\xa00."
            in response.data["employee_number"]
        )
        assert "Ce champ ne peut être vide." in response.data["last_name"]
        assert (
            "La saisie doit comporter uniquement des caractères alphabétiques avec apostrophe, tiret et espace."
            in response.data["first_name"]
        )
        assert "«\xa0?\xa0» n'est pas un choix valide." in response.data["department"]
        assert "Saisissez une adresse e-mail valide." in response.data["user"]["email"]
        assert "Ce champ est obligatoire." in response.data["user"]["password2"]

    def test_post_employees_route_failed_with_forbidden(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a support employee valid token and valid data
        WHEN the employees endpoint is posted to (POST)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["support_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse("employees"), headers=headers, data=self.valid_data, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Employee.objects.count() == 3
        assert CustomUser.objects.count() == 3
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_post_employees_route_failed_with_unauthorized(self, db, api_client, employees_users_with_tokens):
        """
        GIVEN an invalid token and valid data
        WHEN the employees endpoint is posted to (POST)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(
            reverse("employees"), headers=headers, data=self.valid_data, format="json"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Employee.objects.count() == 3
        assert CustomUser.objects.count() == 3
        assert "token_not_valid" in response.data["code"]
