from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


CustomUser = get_user_model()


class TestLogin(APITestCase):
    """
    GIVEN a new user api login url
    WHEN user tries to login
    THEN checks that the response is valid and data are displayed
    """

    def setUp(self):
        self.url = reverse("login")
        CustomUser.objects.create_user("testloginuser@email.com", "123456789!")

    def test_login_route_success(self):
        """
        GIVEN existing user data for login
        WHEN the login endpoint is posted to (POST)
        THEN checks that response is 200 and tokens are displayed
        """
        data = {"email": "testloginuser@email.com", "password": "123456789!"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_route_failed_with_bad_request(self):
        """
        GIVEN wrong user data for login
        WHEN the login endpoint is posted to (POST)
        THEN checks that response is 400 and error message is displayed
        """
        data = {"email": "testloginuser@email.com"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 400)
        assert "Ce champ est obligatoire." in response.data["password"]

    def test_login_route_failed_with_unauthorized(self):
        """
        GIVEN invalid user data for login
        WHEN the login endpoint is posted to (POST)
        THEN checks that response is 401 and error message is displayed
        """
        data = {"email": "unknown@email.com", "password": "123456789!"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 401)
        assert (
            "No active account found with the given credentials"
            in response.data["detail"]
        )

    def test_login_route_failed_with_method_not_allowed(self):
        """
        GIVEN existing user data for login
        WHEN the login endpoint is requested (GET)
        THEN checks that response is 405 and error message is displayed
        """
        data = {"email": "testloginuser@email.com", "password": "123456789!"}
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, 405)
        assert "Méthode «\xa0GET\xa0» non autorisée." in response.data["detail"]


class TestLogout:
    """
    GIVEN a fixture for employees with their associated users and access-refresh tokens
    WHEN user tries to logout
    THEN checks that the response is valid
    """

    def test_logout_route_success(self, api_client, employees_users_with_tokens):
        """
        GIVEN a fixture for management employees with valid token
        WHEN the logout endpoint is posted to (POST)
        THEN checks that response is 205 (tokens are blacklisted)
        """
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(reverse("logout"), headers=headers)
        assert response.status_code == status.HTTP_205_RESET_CONTENT

    def test_logout_route_unauthorized(self, api_client):
        """
        GIVEN an invalid acces token
        WHEN the logout endpoint is posted to (POST)
        THEN checks that response is 401 and error message is displayed
        """
        access_token = "invalid"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.post(reverse("logout"), headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "token_not_valid" in response.data["code"]

    def test_logout_route_failed_with_method_not_allowed(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a fixture for management employees with valid token
        WHEN the logout endpoint is requested (GET)
        THEN checks that response is 405 and error message is displayed
        """
        access_token = employees_users_with_tokens[
            "management_employee"
        ].user.access_token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = api_client.get(reverse("logout"), headers=headers)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


class TestTokenRefresh:
    """
    GIVEN fixture for employees with their associated users and tokens
    WHEN user tries to refresh his token
    THEN checks that the response is valid and data are displayed
    """

    def test_token_refresh_route_success(self, api_client, employees_users_with_tokens):
        """
        GIVEN a fixture for management employees with valid token
        WHEN the token_refresh endpoint is posted to (POST)
        THEN checks that response is 200 and tokens are displayed
        """
        refresh_token = employees_users_with_tokens[
            "management_employee"
        ].user.refresh_token
        data = {"refresh": refresh_token}
        response = api_client.post(reverse("token_refresh"), data=data)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_token_refresh_route_failed_with_bad_request(self, api_client):
        """
        GIVEN empty field refresh token
        WHEN the token_refresh endpoint is posted to (POST)
        THEN checks that response is 400 and error message is displayed
        """
        data = {"refresh": ""}
        response = api_client.post(reverse("token_refresh"), data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Ce champ ne peut être vide." in response.data["refresh"]

    def test_token_refresh_route_failed_with_unauthorized(self, api_client):
        """
        GIVEN an invalid refresh token
        WHEN the token_refresh endpoint is posted to (POST)
        THEN checks that response is 401 and error message is displayed
        """
        data = {"refresh": "WRONGTOKEN"}
        response = api_client.post(reverse("token_refresh"), data=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "token_not_valid" in response.data["code"]

    def test_token_refresh_route_failed_with_method_not_allowed(
        self, api_client, employees_users_with_tokens
    ):
        """
        GIVEN a fixture for management employees with valid token
        WHEN the token_refresh endpoint is requested (GET)
        THEN checks that response is 405 and error message is displayed
        """
        refresh_token = employees_users_with_tokens[
            "management_employee"
        ].user.refresh_token
        data = {"refresh": refresh_token}
        response = api_client.get(reverse("token_refresh"), data=data)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert "Méthode «\xa0GET\xa0» non autorisée." in response.data["detail"]
