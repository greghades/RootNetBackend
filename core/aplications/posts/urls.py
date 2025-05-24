from django.urls import path
from .views import (
    ListPostsOwnerView,
    ListPostsFeedView,
    CreatePostView,
    UpdatePostView,
    DeletePostView,
    CommentsView,
    LikePostView,
    FavoritePostView
)

urlpatterns = [
    path("get-posts/", ListPostsFeedView.as_view(), name="post-list"),
    path("get-owner-posts/", ListPostsOwnerView.as_view(), name="post-owner"),
    path("create/", CreatePostView.as_view(), name="post-create"),
    path("update/<int:post_id>/", UpdatePostView.as_view(), name="post-update"),
    path("delete/<int:post_id>/", DeletePostView.as_view(), name="post-delete"),
    # Comments
    path("comments/", CommentsView.as_view(), name="comment-service"),
    # Likes
    path("like/<int:post_id>/", LikePostView.as_view(), name="like-service"),
    # Favorites
    path("favorites/", FavoritePostView.as_view(), name="favorite-service"),
]
