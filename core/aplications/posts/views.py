from django.shortcuts import render
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView,DestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .serializers import PostSerializer, SocialMediaCursorPagination
from .models import Post, Comment, Like
# Create your views here.
from rest_framework.authentication import TokenAuthentication



class ListPostsView(ListAPIView):
    """
    View to list all posts.
    """
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    pagination_class = SocialMediaCursorPagination

class CreatePostView(CreateAPIView):
    """
    View to create a new post.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer



class UpdatePostView(RetrieveUpdateAPIView):
    """
    View to update or delete a post.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    queryset = Post.objects.all()

class DeletePostView(DestroyAPIView):
    """
    View to delete a post.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    queryset = Post.objects.all()
