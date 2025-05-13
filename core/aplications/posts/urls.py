from django.urls import path
from .views import (
    ListPostsView,
    CreatePostView,
    UpdatePostView,
    DeletePostView,
)

urlpatterns = [
    path('get-posts/', ListPostsView.as_view(), name='post-list'),
    path('create/', CreatePostView.as_view(), name='post-create'),
    path('update/<int:pk>/', UpdatePostView.as_view(), name='post-update'),
    path('delete/<int:pk>/', DeletePostView.as_view(), name='post-delete'),
]
