# users/urls.py
from django.urls import path

from .views import (
    FollowUserView,
    ProfileSettingsView,
    UnfollowUserView,
    UserProfileView,
)

urlpatterns = [
    path("profile/", ProfileSettingsView.as_view(), name="profile"),
    path("follow/", FollowUserView.as_view(), name="follow"),
    path("unfollow/", UnfollowUserView.as_view(), name="unfollow"),
    path("user/<str:username>/", UserProfileView.as_view(), name="user-profile"),
]
