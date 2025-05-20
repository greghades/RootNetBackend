from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser

# Create your tests here.


class AuthenticationTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
        )

    def test_login(self):
        # Test the login functionality
        url = reverse("login")
        data = {
            "email": "testuser@example.com",
            "password": "testpassword",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        # Test login with invalid credentials
        url = reverse("login")
        data = {
            "email": "testuser@example.com",
            "password": "wrongpassword",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["Message"],
            "invalid credentials",
        )
    
    def sing_up(self):
        # Test the signup functionality
        url = reverse("signup")
        data = {
            "email": "testuser@example.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertIn("message", response.data)

    def test_logout(self):
        # Test the logout functionality
        url_login = reverse("login")
        data = {
            "email": "testuser@example.com",
            "password": "testpassword",
        }
        response = self.client.post(url_login, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

        refresh_token = RefreshToken(response.data["refresh"])
        jti = refresh_token["jti"]

        url_logout = reverse("logout")
        data = {
            "refresh": response.data["refresh"],
        }
        response = self.client.post(
            url_logout,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}",
        )
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        blacklisted = BlacklistedToken.objects.filter(
            token__jti=jti,
        ).exists()
        self.assertTrue(blacklisted)
