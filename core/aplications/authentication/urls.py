from django.urls import path

from .views import (

    LoginView,
    LogoutView,
    ResetPasswordView,
    SendCodeResetPassword,
    SignUpView,
    UpdateCurrentUserView,
    ValidationCodeView,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("send-code/", SendCodeResetPassword.as_view(), name="send-code"),
    path("validate-code/", ValidationCodeView.as_view(), name="validate-code"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path("update-current-user/", UpdateCurrentUserView.as_view(), name="update-current-user"
    
    ),
]
