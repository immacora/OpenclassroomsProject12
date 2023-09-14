from django.contrib.auth import get_user_model
from rest_framework import status
from django.urls import reverse

from accounts.models import Employee

CustomUser = get_user_model()


class TestGetEmployee:
    """
    GIVEN fixture for employees with their associated users and tokens
    WHEN user tries to get an employee via id
    THEN checks that the response is valid and data are displayed
    """

    def test_get_employee_route_success(self, api_client, employees_users_with_tokens):
        """
        GIVEN a management employee valid token and a valid employee_id
        WHEN the employee endpoint is requested (GET)
        THEN checks that response is 200 and datas are displayed
        """
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        employee_to_get = employees_users_with_tokens["sales_employee"]
        employee_id = employee_to_get.employee_id
        response = api_client.get(
            reverse("employee_detail", kwargs={"employee_id": employee_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert Employee.objects.count() == 3
        assert CustomUser.objects.count() == 3
        assert str(employee_id) in response.data["employee_id"]
        assert employee_to_get.employee_number == response.data["employee_number"]
        assert employee_to_get.last_name in response.data["last_name"]
        assert employee_to_get.first_name in response.data["first_name"]
        assert "SALES" in response.data["department"]
        assert str(employee_to_get.user.user_id) in response.data["user"]["user_id"]
        assert employee_to_get.user.email in response.data["user"]["email"]
        assert employee_to_get.user.is_active == response.data["user"]["is_active"]
        assert employee_to_get.user.is_staff == response.data["user"]["is_staff"]
        assert "date_joined" in response.data["user"]
        assert "created_at" in response.data
        assert "updated_at" in response.data

    def test_get_employee_route_failed_with_forbidden(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a sales employee valid token and a valid employee_id
        WHEN the employee endpoint is requested (GET)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["support_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        employee_to_get = employees_users_with_tokens["sales_employee"]
        employee_id = employee_to_get.employee_id
        response = api_client.get(
            reverse("employee_detail", kwargs={"employee_id": employee_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Employee.objects.count() == 3
        assert CustomUser.objects.count() == 3
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )
        assert "employee_id" not in response.data

    def test_get_employee_route_failed_with_unauthorized(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN an invalid token and a valid employee_id
        WHEN the employee endpoint is requested (GET)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        employee_to_get = employees_users_with_tokens["sales_employee"]
        employee_id = employee_to_get.employee_id
        response = api_client.get(
            reverse("employee_detail", kwargs={"employee_id": employee_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Employee.objects.count() == 3
        assert CustomUser.objects.count() == 3
        assert "token_not_valid" in response.data["code"]


class TestPutEmployee:
    """
    GIVEN fixture for employees with their associated users and tokens
    WHEN user tries to edit an employee and his related user via id
    THEN checks that the response is valid and data are displayed
    """

    valid_data = {
        "employee_number": "963",
        "first_name": "UPDATED Admin TEST prénom",
        "last_name": "UPDATED Admin TEST nom",
        "department": "SALES",
        "user": {"email": "UPDATEDadminTEST@email.com", "is_active": "False"},
    }
    invalid_employee_data = {
        "employee_number": "f",
        "first_name": "/Admin TEST prénom",
        "last_name": "<Admin TEST nom",
        "department": "WRONG",
        "user": {"email": "adminTEST@email.com", "is_active": "True"},
    }

    def test_put_employee_route_success(self, api_client, employees_users_with_tokens):
        """
        GIVEN a management employee valid token, a valid employee_id and valid data
        WHEN the employee endpoint is updated to (PUT)
        THEN checks that response is 200 and datas are displayed
        """
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        employee_to_update = employees_users_with_tokens["sales_employee"]
        employee_id = employee_to_update.employee_id
        response = api_client.put(
            reverse("employee_detail", kwargs={"employee_id": employee_id}),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert Employee.objects.count() == 3
        assert CustomUser.objects.count() == 3
        assert str(employee_id) in response.data["employee_id"]
        assert 963 == response.data["employee_number"]
        assert "UPDATED Admin TEST nom" in response.data["last_name"]
        assert "UPDATED Admin TEST prénom" in response.data["first_name"]
        assert "SALES" in response.data["department"]
        assert str(employee_to_update.user.user_id) in response.data["user"]["user_id"]
        assert "UPDATEDadminTEST@email.com" in response.data["user"]["email"]
        assert False == response.data["user"]["is_active"]  # noqa: E712
        assert False == response.data["user"]["is_staff"]  # noqa: E712
        assert "date_joined" in response.data["user"]
        assert "created_at" in response.data
        assert "updated_at" in response.data

    def test_put_employee_route_failed_with_bad_request(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a management employee valid token, a valid employee_id and invalid data
        WHEN the employee endpoint is updated to (PUT)
        THEN checks that response is 400 and error message is displayed
        """
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        employee_to_update = employees_users_with_tokens["sales_employee"]
        employee_id = employee_to_update.employee_id
        response = api_client.put(
            reverse("employee_detail", kwargs={"employee_id": employee_id}),
            headers=headers,
            data=self.invalid_employee_data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Employee.objects.count() == 3
        assert CustomUser.objects.count() == 3
        assert "Un nombre entier valide est requis." in response.data["employee_number"]
        assert (
            "La saisie doit comporter uniquement des caractères alphabétiques avec apostrophe, tiret et espace."
            in response.data["last_name"]
        )
        assert (
            "La saisie doit comporter uniquement des caractères alphabétiques avec apostrophe, tiret et espace."
            in response.data["first_name"]
        )
        assert (
            "«\xa0WRONG\xa0» n'est pas un choix valide." in response.data["department"]
        )

    def test_put_employee_route_failed_with_forbidden(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a support employee valid token, a valid employee_id and valid data
        WHEN the employee endpoint is updated to (PUT)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["support_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        employee_to_update = employees_users_with_tokens["sales_employee"]
        employee_id = employee_to_update.employee_id
        response = api_client.put(
            reverse("employee_detail", kwargs={"employee_id": employee_id}),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Employee.objects.count() == 3
        assert CustomUser.objects.count() == 3
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_put_employee_failed_with_unauthorized(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN an invalid token, a valid employee_id and valid data
        WHEN the employee endpoint is updated to (PUT)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        employee_to_update = employees_users_with_tokens["sales_employee"]
        employee_id = employee_to_update.employee_id
        response = api_client.put(
            reverse("employee_detail", kwargs={"employee_id": employee_id}),
            headers=headers,
            data=self.valid_data,
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Employee.objects.count() == 3
        assert CustomUser.objects.count() == 3
        assert "token_not_valid" in response.data["code"]


class TestDeleteEmployee:
    """
    GIVEN fixture for employees with their associated users and tokens
    WHEN user tries to delete an employee and his linked user via id
    THEN checks that the response is valid and data are displayed
    """

    def test_delete_employee_route_success(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a management employee valid token and a valid employee_id
        WHEN the employee endpoint is deleted (DEL)
        THEN checks that response is 204
        """
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        employee_to_delete = employees_users_with_tokens["sales_employee"]
        employee_id = employee_to_delete.employee_id
        response = api_client.delete(
            reverse("employee_detail", kwargs={"employee_id": employee_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Employee.objects.count() == 2
        assert CustomUser.objects.count() == 2

    def test_delete_employee_route_failed_with_forbidden(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a support employee valid token and a valid employee_id
        WHEN the employee endpoint is deleted (DEL)
        THEN checks that response is 403 and error message is displayed
        """
        access_token = employees_users_with_tokens["support_employee"].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        employee_to_delete = employees_users_with_tokens["sales_employee"]
        employee_id = employee_to_delete.employee_id
        response = api_client.delete(
            reverse("employee_detail", kwargs={"employee_id": employee_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Employee.objects.count() == 3
        assert CustomUser.objects.count() == 3
        assert (
            "Vous n'avez pas la permission d'effectuer cette action."
            in response.data["detail"]
        )

    def test_delete_employee_route_failed_with_unauthorized(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN an invalid token and a valid employee_id
        WHEN the employee endpoint is deleted (DEL)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "INVALIDTOKEN"
        headers = {"Authorization": f"Bearer {access_token}"}
        employee_to_delete = employees_users_with_tokens["sales_employee"]
        employee_id = employee_to_delete.employee_id
        response = api_client.delete(
            reverse("employee_detail", kwargs={"employee_id": employee_id}),
            headers=headers,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Employee.objects.count() == 3
        assert CustomUser.objects.count() == 3
        assert "token_not_valid" in response.data["code"]

    def test_delete_employee_route_failed_with_not_found(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a management employee valid token and a invalid employee_id
        WHEN the employee endpoint is deleted (DEL)
        THEN checks that response is 404 and error message is displayed
        """
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.delete("api/employees/1234/", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Employee.objects.count() == 3
        assert CustomUser.objects.count() == 3
