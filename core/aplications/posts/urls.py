from django.urls import path
from .views import (
    ListPostsView,
    CreatePostView,
    UpdatePostView,
    DeletePostView,
    CommentsView,
    LikePostView,
    FavoritePostView
)

urlpatterns = [
    path("get-posts/", ListPostsView.as_view(), name="post-list"),
    path("create/", CreatePostView.as_view(), name="post-create"),
    path("update/<int:pk>/", UpdatePostView.as_view(), name="post-update"),
    path("delete/<int:pk>/", DeletePostView.as_view(), name="post-delete"),
    # Comments
    path("comments/", CommentsView.as_view(), name="comment-service"),
    # Likes
    path("like/<int:post_id>/", LikePostView.as_view(), name="like-service"),
    # Favorites
    path("favorites/", FavoritePostView.as_view(), name="favorite-service"),
]
