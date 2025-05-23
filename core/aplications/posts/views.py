from django.shortcuts import render
from rest_framework import status

# Create your views here.
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Like, Post
from .serializers import CommentSerializer, PostSerializer, SocialMediaCursorPagination


class ListPostsView(ListAPIView):
    """
    View to list all posts.
    """

    serializer_class = PostSerializer
    queryset = Post.objects.all()
    pagination_class = SocialMediaCursorPagination


class CreatePostView(CreateAPIView):
    """
    View to create a new post.
    """

    serializer_class = PostSerializer


class UpdatePostView(RetrieveUpdateAPIView):
    """
    View to update or delete a post.
    """

    serializer_class = PostSerializer
    queryset = Post.objects.all()


class DeletePostView(DestroyAPIView):
    """
    View to delete a post.
    """

    serializer_class = PostSerializer
    queryset = Post.objects.all()


# Create a new comment


class CommentsView(APIView):

    def get(self, request, *args, **kwargs):

        post_id = request.query_params.get("post_id", None)

        if not post_id:
            return Response(
                {"error": "post_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            post = Post.objects.get(id=post_id)
            comments = Comment.objects.filter(post=post)

            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request, *args, **kwargs):

        post_id = request.data.get("post_id", None)
        content = request.data.get("content", None)

        if not post_id or not content:
            return Response(
                {"error": "post_id and content are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            post = Post.objects.get(id=post_id)
            Comment.objects.create(author=request.user, post=post, content=content)

            return Response(
                {
                    "message": "Comment created successfully",
                },
                status=status.HTTP_201_CREATED,
            )
        except Post.DoesNotExist:
            return Response(
                {
                    "message": "Post not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def patch(self, request, *args, **kwargs):

        comment_id = request.data.get("comment_id", None)
        content = request.data.get("content", None)

        if not comment_id or not content:
            return Response(
                {"error": "comment_id and content are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            comment = Comment.objects.get(id=comment_id)
            comment.content = content
            comment.save()

            return Response(
                {
                    "message": "Comment updated successfully",
                },
                status=status.HTTP_200_OK,
            )
        except Comment.DoesNotExist:
            return Response(
                {
                    "message": "Comment not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, *args, **kwargs):
        comment_id = request.data.get("comment_id", None)

        if not comment_id:
            return Response(
                {"error": "comment_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            comment = Comment.objects.get(id=comment_id)
            comment.delete()

            return Response(
                {
                    "message": "Comment deleted successfully",
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        except Comment.DoesNotExist:
            return Response(
                {
                    "message": "Comment not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
