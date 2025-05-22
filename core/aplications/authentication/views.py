from datetime import datetime

from django.contrib.auth import authenticate
from django.core.mail import EmailMultiAlternatives
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
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
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UpdateCurrentUserView(generics.GenericAPIView):
    serializer_class = UserTokenSerializer

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"user": serializer.data, "message": "Usuario actualizado correctamente."},
            status=status.HTTP_200_OK,
        )


class SendCodeResetPassword(generics.GenericAPIView):

    def post(self, request):
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
    def post(self, request):
        code_request = request.data.get("code", None)
        try:
            code_database = CodesVerification.objects.get(
                changePasswordCode=code_request
            )
            serializerValidate = ValidateCodeSerializer(code_database)
            if code_database is not None:
                CodesVerification.delete(code_database)

                return Response(
                    {
                        "Validated": CODE_VALIDATED,
                        "Entity": serializerValidate.data,
                    },
                    status=status.HTTP_202_ACCEPTED,
                )
        except:
            return Response(
                CODER_VERIFICATION_ERROR, status=status.HTTP_401_UNAUTHORIZED
            )


class ResetPasswordView(generics.GenericAPIView):
    def post(self, request):

        new_password = request.data.get("new_password", None)
        confirm_new_password = request.data.get("confirm_password", None)

        if new_password is not None and confirm_new_password is not None:
            if new_password != confirm_new_password:
                return Response(
                    PASSWORD_MUST_BE_SAME,
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = CustomUser.objects.get(id=request.user.id)
            user.set_password(new_password)
            user.save()
            return Response(PASSWORD_CHANGED, status=status.HTTP_200_OK)
        else:
            return Response(CHANGED_PASSWORD_ERROR, status=status.HTTP_400_BAD_REQUEST)
