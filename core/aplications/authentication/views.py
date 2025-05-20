from datetime import datetime

from django.contrib.auth import authenticate, logout
from django.contrib.sessions.models import Session
from django.core.mail import EmailMultiAlternatives
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from settings.base import EMAIL_HOST_USER

from .helpers.content_emails import PASSWORD_RESET
from .helpers.randCodes import generatedCode
from .messages.responses_error import (
    CHANGED_PASSWORD_ERROR,
    CODER_VERIFICATION_ERROR,
    LOGIN_CREDENTIALS_ERROR,
    LOGIN_CREDENTIALS_REQUIRED_ERROR,
    LOGOUT_ERROR,
    NOT_FOUND_USER,
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
    UserSerializer,
    UserTokenSerializer,
    ValidateCodeSerializer,
    RegisterSerializer,
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


class UpdateUser(generics.RetrieveUpdateAPIView):

    serializer_class = UserTokenSerializer
    queryset = CustomUser.objects.all()

    def put(self, request, *args, **kwargs):

        return Response(
            {"data": request.data, "message": UPDATE_OK},
            status=status.HTTP_202_ACCEPTED,
        )


class ListUsers(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.order_by("id")


class DeleteView(generics.GenericAPIView):

    def delete(self, request, pk):
        user = CustomUser.objects.get(id=pk)
        if user:
            user.delete()
            return Response(DELETED_USER, status=status.HTTP_200_OK)
        else:
            return Response(NOT_FOUND_USER, status=status.HTTP_404_NOT_FOUND)


class SendCodeResetPassword(generics.GenericAPIView):

    def post(self, request):
        email = request.data.get("email", None)
        try:
            user = CustomUser.objects.get(email=email)
            if user:
                mailReset = EmailMultiAlternatives(
                    "Reset password", "Abroad", EMAIL_HOST_USER, [email]
                )

                code = CodesVerification(changePasswordCode=generatedCode(), user=user)
                code.save()

                mailReset.attach_alternative(
                    f"<h1>Your verification Code: {code.changePasswordCode}</h1>",
                    "text/html",
                )
                mailReset.send()

                return Response(EMAIL_SEND, status=status.HTTP_200_OK)
        except:
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
        userId = request.data.get("user", None)
        new_password = request.data.get("password", None)
        if new_password is not None and userId is not None:
            user = CustomUser.objects.get(id=userId)
            user.set_password(new_password)
            user.save()
            return Response(PASSWORD_CHANGED, status=status.HTTP_200_OK)
        else:
            return Response(CHANGED_PASSWORD_ERROR, status=status.HTTP_400_BAD_REQUEST)
