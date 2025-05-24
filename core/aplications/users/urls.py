# users/urls.py
from django.urls import path
from .views import FollowUserView, UnfollowUserView,ProfileView

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("follow/", FollowUserView.as_view(), name="follow"),
    path("unfollow/", UnfollowUserView.as_view(), name="unfollow"),
]
