from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CodesVerification, CustomUser, Reset_password

# Create your tests here.


class AuthenticationTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
        )
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
        }

    def _login_user(self, email=None, password=None):
        # Helper method to log in the user and get the access token
        url = reverse("login")
        data = {
            "email": email or self.user_data["email"],
            "password": password or self.user_data["password"],
        }
        response = self.client.post(url, data, format="json")
        return response

    def test_login(self):
        # Test the login functionality
        response = self._login_user()

        access_token = response.data.get("access")
        refresh_token = response.data.get("refresh")

        self.assertIsNotNone(access_token)
        self.assertIsNotNone(refresh_token)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        # Test login with invalid credentials
        response = self._login_user(
            email="testuser@example.com", password="wrongpassword"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["Message"],
            "invalid credentials",
        )

    def sign_up(self):
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
        response = self._login_user()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refresh_token = response.data["refresh"]

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

    def test_send_password_reset_email(self):
        # Test sending password reset email

        response = self._login_user()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse("send-code")
        data = {
            "email": "testuser@example.com",
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}",
        )
        self.assertEqual(response.data["Message"], "Email Send")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_validate_code(self):
        # Test validating the password reset code
        url = reverse("validate-code")
        response = self._login_user()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        code = CodesVerification.objects.create(
            changePasswordCode="123456",
            user=self.user,
        )
        data = {"code": code.changePasswordCode}

        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data["Validated"], True)

    def test_reset_password(self):
        # Test resetting the password
        url = reverse("reset-password")

        response = self._login_user()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {
            "new_password": "newpassword123",
            "confirm_password": "newpassword123",
        }

        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["Message"], "Password changed successfully")

    def test_password_must_be_same(self):
        # Test that the new password and confirm password must be the same
        url = reverse("reset-password")

        response = self._login_user()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {
            "new_password": "newpassword123",
            "confirm_password": "differentpassword",
        }

        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["Message"],
            "The new password must be the same as the old one",
        )
