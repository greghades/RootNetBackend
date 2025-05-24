from datetime import datetime

from django.contrib.auth import authenticate
from django.core.mail import EmailMultiAlternatives
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from settings.base import EMAIL_HOST_USER

from .helpers.content_emails import get_email_content
from .helpers.randCodes import generatedCode
from .messages.responses_error import (
    CHANGED_PASSWORD_ERROR,
    CODER_VERIFICATION_ERROR,
    LOGIN_CREDENTIALS_ERROR,
    LOGIN_CREDENTIALS_REQUIRED_ERROR,
    LOGOUT_ERROR,
    NOT_FOUND_USER,
    PASSWORD_MUST_BE_SAME,
)
from .messages.responses_ok import (
    CODE_VALIDATED,
    DELETED_USER,
    EMAIL_SEND,
    LOGIN_OK,
    LOGOUT_OK,
    PASSWORD_CHANGED,
    SIGNUP_OK,
    UPDATE_OK,
)
from .models import CodesVerification, CustomUser
from .serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
    UserTokenSerializer,
    ValidateCodeSerializer,
)

# Create your views here.


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_summary="Login",
        operation_description="Authenticate user and return JWT tokens.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="User email"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="User password"
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "access": "token",
                        "refresh": "token",
                        "user": {},
                        "message": "Login OK",
                    }
                },
            ),
            401: openapi.Response(description="Invalid credentials"),
        },
    )
    def post(self, request, *args, **kwargs):

        email = request.data.get("email", None)
        password = request.data.get("password", None)
        user = authenticate(username=email, password=password)

        if user:
            login_serializer = self.get_serializer(data=request.data)
            if login_serializer.is_valid():

                user_serializer = UserSerializer(user)
                return Response(
                    {
                        "access": login_serializer.validated_data["access"],
                        "refresh": login_serializer.validated_data["refresh"],
                        "user": user_serializer.data,
                        "message": LOGIN_OK,
                    },
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                LOGIN_CREDENTIALS_ERROR, status=status.HTTP_401_UNAUTHORIZED
            )


class SignUpView(generics.GenericAPIView):

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_summary="Sign up",
        operation_description="Register a new user.",
        request_body=RegisterSerializer,
        responses={
            200: openapi.Response(
                description="User registered",
                examples={"application/json": {"user": {}, "message": "Sign up OK"}},
            ),
            400: openapi.Response(description="Bad request"),
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "message": SIGNUP_OK,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(generics.GenericAPIView):
    

    @swagger_auto_schema(
        operation_summary="Logout",
        operation_description="Blacklist the refresh token to logout.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Refresh token"
                ),
            },
        ),
        responses={
            205: openapi.Response(description="Logout successful"),
            400: openapi.Response(description="Bad request"),
        },
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ListUsers(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.order_by("id")

    @swagger_auto_schema(
        operation_summary="List users",
        operation_description="List all users.",
        responses={200: UserSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DeleteView(generics.GenericAPIView):

    @swagger_auto_schema(
        operation_summary="Delete user",
        operation_description="Delete a user by ID.",
        manual_parameters=[
            openapi.Parameter(
                "pk",
                openapi.IN_PATH,
                description="User ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(description="User deleted"),
            404: openapi.Response(description="User not found"),
        },
    )
    def delete(self, request, pk):
        user = CustomUser.objects.get(id=pk)
        if user:
            user.delete()
            return Response(DELETED_USER, status=status.HTTP_200_OK)
        else:
            return Response(NOT_FOUND_USER, status=status.HTTP_404_NOT_FOUND)


class SendCodeResetPassword(generics.GenericAPIView):
    """
    Vista para enviar un código de recuperación de contraseña al correo del usuario.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Enviar código de recuperación",
        operation_description="Envía un código de recuperación de contraseña al correo electrónico del usuario.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email"],
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Correo electrónico del usuario"
                ),
            },
        ),
        responses={
            200: openapi.Response(description="Correo enviado"),
            401: openapi.Response(description="Credenciales inválidas"),
        },
    )
    def post(self, request):
        """
        Envía un código de recuperación de contraseña al correo del usuario si existe.
        """
        email = request.data.get("email", None)
        try:
            user = CustomUser.objects.get(email=email)
            if user:
                mailReset = EmailMultiAlternatives(
                    "Reset password", "Rootnet Service", EMAIL_HOST_USER, [email]
                )

                code = CodesVerification(changePasswordCode=generatedCode(), user=user)
                code.save()

                mailReset.attach_alternative(get_email_content(code), "text/html")
                mailReset.send()

                return Response(EMAIL_SEND, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(
                LOGIN_CREDENTIALS_ERROR, status=status.HTTP_401_UNAUTHORIZED
            )


class ValidationCodeView(generics.GenericAPIView):
    """
    Vista para validar el código de recuperación enviado al correo del usuario.
    """
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_summary="Validar código de recuperación",
        operation_description="Valida el código de recuperación enviado al correo electrónico del usuario.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["code"],
            properties={
                "code": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Código de verificación recibido por correo"
                ),
            },
        ),
        responses={
            202: openapi.Response(description="Código validado"),
            401: openapi.Response(description="Código inválido o expirado"),
        },
    )
    def post(self, request):
        """
        Valida el código de recuperación. Si es correcto y no ha sido usado, lo marca como usado.
        """
        code_request = request.data.get("code", None)
        try:
            code_database = CodesVerification.objects.get(
                changePasswordCode=code_request, is_used=False  # Solo códigos no usados
            )
            # Marca el código como validado (usado)
            code_database.is_used = True
            code_database.dateUsed = datetime.now()
            code_database.save()

            serializerValidate = ValidateCodeSerializer(code_database)
            return Response(
                {
                    "Validated": CODE_VALIDATED,
                    "Entity": serializerValidate.data,
                },
                status=status.HTTP_202_ACCEPTED,
            )
        except CodesVerification.DoesNotExist:
            return Response(
                CODER_VERIFICATION_ERROR, status=status.HTTP_401_UNAUTHORIZED
            )


class ResetPasswordView(generics.GenericAPIView):
    """
    Vista para cambiar la contraseña del usuario usando un código previamente validado.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Restablecer contraseña",
        operation_description="Permite al usuario cambiar su contraseña si el código de recuperación fue validado.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["code", "email", "new_password", "confirm_password"],
            properties={
                "code": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Código de verificación validado"
                ),
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Correo electrónico del usuario"
                ),
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Nueva contraseña"
                ),
                "confirm_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Confirmación de la nueva contraseña"
                ),
            },
        ),
        responses={
            200: openapi.Response(description="Contraseña cambiada"),
            400: openapi.Response(description="Datos inválidos o contraseñas no coinciden"),
            401: openapi.Response(description="Código inválido o expirado"),
            404: openapi.Response(description="Usuario no encontrado"),
        },
    )
    def post(self, request):
        """
        Cambia la contraseña del usuario si el código fue validado y no ha sido usado antes.
        El código se elimina después de usarse para mayor seguridad.
        """
        code = request.data.get("code", None)
        email = request.data.get("email", None)
        new_password = request.data.get("new_password", None)
        confirm_new_password = request.data.get("confirm_password", None)

        if not all([code, email, new_password, confirm_new_password]):
            return Response(CHANGED_PASSWORD_ERROR, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_new_password:
            return Response(
                PASSWORD_MUST_BE_SAME,
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = CustomUser.objects.get(email=email)
            code_obj = CodesVerification.objects.get(
                changePasswordCode=code,
                user=user,
                is_used=True,  # Solo códigos ya validados
            )
            # Cambia la contraseña solo si el código fue validado
            user.set_password(new_password)
            user.save()
            code_obj.delete()  # Elimina el código después de usarlo
            return Response(PASSWORD_CHANGED, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response(NOT_FOUND_USER, status=status.HTTP_404_NOT_FOUND)
        except CodesVerification.DoesNotExist:
            return Response(
                CODER_VERIFICATION_ERROR, status=status.HTTP_401_UNAUTHORIZED
            )


class ChangePasswordView(generics.GenericAPIView):
    """
    Vista para que el usuario autenticado cambie su contraseña desde los ajustes.
    """

    
    @swagger_auto_schema(
        operation_summary="Cambiar contraseña (ajustes)",
        operation_description="Permite al usuario autenticado cambiar su contraseña proporcionando la contraseña actual y la nueva.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["current_password", "new_password", "confirm_password"],
            properties={
                "current_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Contraseña actual"
                ),
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Nueva contraseña"
                ),
                "confirm_password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Confirmación de la nueva contraseña",
                ),
            },
        ),
        responses={
            200: openapi.Response(description="Contraseña cambiada correctamente"),
            400: openapi.Response(
                description="Datos inválidos o contraseñas no coinciden"
            ),
            401: openapi.Response(description="Contraseña actual incorrecta"),
        },
        security=[{"Bearer": []}],
    )
    def post(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not user.check_password(current_password):
            return Response(
                {"error": "Contraseña actual incorrecta."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if new_password != confirm_password:
            return Response(
                {"error": "Las contraseñas no coinciden."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save()
        return Response(
            {"message": "Contraseña cambiada correctamente."}, status=status.HTTP_200_OK
        )
