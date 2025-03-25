from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


class RegisterViewTests(TestCase):
    """
    Test cases for user registration
    """

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("register")

    def test_register_success(self):
        data = {
            "username": "testuser",
            "password": "testpassword",
            "email": "testuser@example.com",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), {"message": "User registered successfully"})
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_register_missing_field(self):
        data = {
            "username": "testuser",
            "password": "testpassword",
            # Missing email
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({"error": "Missing fields: email"}, response.json())

    def test_register_username_taken(self):
        User.objects.create_user(
            username="testuser", password="testpassword", email="testuser@example.com"
        )
        data = {
            "username": "testuser",
            "password": "testpassword",
            "email": "anotheruser@example.com",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Username already exists"})

    def test_register_missing_fields(self):
        data = {}
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(
            response_data["error"], "Missing fields: username, password, email"
        )


class LoginViewTests(TestCase):
    """
    Test cases for user registration
    """

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", email="testuser@example.com"
        )

    def test_login_and_logout_success(self):
        login_data = {
            "username": "testuser",
            "password": "testpassword",
        }
        self.assertTrue(
            User.objects.filter(
                username="testuser", email="testuser@example.com"
            ).exists()
        )

        login_response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        data = login_response.json()
        decoded_token = AccessToken(data["access"])
        self.assertEqual(decoded_token["user_id"], self.user.id)
        self.assertIsNone(decoded_token.check_exp())

        logout_response = self.client.post(
            self.logout_url,
            {"refresh": data["refresh"]},
            HTTP_AUTHORIZATION=f"Bearer {data['access']}",
            format="json",
        )
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
