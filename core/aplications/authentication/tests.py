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

    def test_reset_password_with_valid_code(self):
        """
        Test para cambiar la contraseña usando un código de verificación válido (usuario no autenticado).
        """
        # Crear código de verificación y asociarlo al usuario
        code = CodesVerification.objects.create(
            changePasswordCode="654321", user=self.user, is_used=False
        )
        # Validar el código (simula el endpoint de validación)
        code.is_used = True
        code.save()

        url = reverse("reset-password")
        data = {
            "code": code.changePasswordCode,
            "email": self.user.email,
            "new_password": "newpassword123",
            "confirm_password": "newpassword123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verifica que la contraseña realmente cambió
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))

    def test_reset_password_with_invalid_code(self):
        """
        Test para intentar cambiar la contraseña con un código inválido.
        """
        url = reverse("reset-password")
        data = {
            "code": "codigo_invalido",
            "email": self.user.email,
            "new_password": "newpassword123",
            "confirm_password": "newpassword123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["Validated"], False
        )

    def test_change_password_authenticated(self):
        """
        Test para cambiar la contraseña desde ajustes (usuario autenticado).
        """
        # Login para obtener token
        login_response = self._login_user()
        access_token = login_response.data["access"]

        url = reverse("change-password")
        data = {
            "current_password": "testpassword",
            "new_password": "nuevoajustes123",
            "confirm_password": "nuevoajustes123",
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Contraseña cambiada correctamente", response.data["message"])

        # Verifica que la contraseña realmente cambió
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("nuevoajustes123"))

    def test_change_password_wrong_current(self):
        """
        Test para intentar cambiar la contraseña desde ajustes con la contraseña actual incorrecta.
        """
        login_response = self._login_user()
        access_token = login_response.data["access"]

        url = reverse("change-password")
        data = {
            "current_password": "incorrecta",
            "new_password": "nuevoajustes123",
            "confirm_password": "nuevoajustes123",
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Contraseña actual incorrecta", response.data["error"])

    def test_change_password_mismatch(self):
        """
        Test para intentar cambiar la contraseña desde ajustes con confirmación incorrecta.
        """
        login_response = self._login_user()
        access_token = login_response.data["access"]

        url = reverse("change-password")
        data = {
            "current_password": "testpassword",
            "new_password": "nuevoajustes123",
            "confirm_password": "diferente",
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Las contraseñas no coinciden", response.data["error"])
