from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
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

    @swagger_auto_schema(
        operation_summary="Retrieve comments for a specific post",
        operation_description="Fetches all comments associated with a given post ID. Requires a valid JWT token.",
        manual_parameters=[
            openapi.Parameter(
                "post_id",
                openapi.IN_QUERY,
                description="ID of the post to retrieve comments for",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: CommentSerializer(many=True),
            400: openapi.Response(
                description="Bad Request",
                examples={"application/json": {"error": "post_id is required."}},
            ),
            404: openapi.Response(
                description="Not Found",
                examples={"application/json": {"error": "Post not found."}},
            ),
        },
        security=[{"Bearer": []}],  # Indica que requiere autenticación JWT
    )
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

    @swagger_auto_schema(
        operation_summary="Create a new comment",
        operation_description="Creates a new comment for a specific post. Requires a valid JWT token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["post_id", "content"],
            properties={
                "post_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the post to comment on",
                ),
                "content": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Content of the comment"
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Comment created",
                examples={
                    "application/json": {"message": "Comment created successfully"}
                },
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {"error": "post_id and content are required."}
                },
            ),
            404: openapi.Response(
                description="Not Found",
                examples={"application/json": {"message": "Post not found"}},
            ),
        },
        security=[{"Bearer": []}],
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
                {"message": "Comment created successfully"},
                status=status.HTTP_201_CREATED,
            )
        except Post.DoesNotExist:
            return Response(
                {"message": "Post not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @swagger_auto_schema(
        operation_summary="Update an existing comment",
        operation_description="Updates the content of a specific comment. Requires a valid JWT token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["comment_id", "content"],
            properties={
                "comment_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID of the comment to update"
                ),
                "content": openapi.Schema(
                    type=openapi.TYPE_STRING, description="New content for the comment"
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Comment updated",
                examples={
                    "application/json": {"message": "Comment updated successfully"}
                },
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "error": "comment_id and content are required."
                    }
                },
            ),
            404: openapi.Response(
                description="Not Found",
                examples={"application/json": {"message": "Comment not found"}},
            ),
        },
        security=[{"Bearer": []}],
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
                {"message": "Comment updated successfully"},
                status=status.HTTP_200_OK,
            )
        except Comment.DoesNotExist:
            return Response(
                {"message": "Comment not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @swagger_auto_schema(
        operation_summary="Delete a comment",
        operation_description="Deletes a specific comment. Requires a valid JWT token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["comment_id"],
            properties={
                "comment_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID of the comment to delete"
                ),
            },
        ),
        responses={
            204: openapi.Response(
                description="Comment deleted",
                examples={
                    "application/json": {"message": "Comment deleted successfully"}
                },
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={"application/json": {"error": "comment_id is required."}},
            ),
            404: openapi.Response(
                description="Not Found",
                examples={"application/json": {"message": "Comment not found"}},
            ),
        },
        security=[{"Bearer": []}],
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
                {"message": "Comment deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Comment.DoesNotExist:
            return Response(
                {"message": "Comment not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class LikePostView(APIView):
    """
    View to like or unlike a post.
    """


    def post(self, request, post_id):
        """
        Like a post.
        """
        try:
            post = Post.objects.get(id=post_id)
            like, created = Like.objects.get_or_create(user=request.user, post=post)

            if created:
                return Response({"message": "Post liked."}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Post already liked."}, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, post_id):
        """
        Unlike a post.
        """
        try:
            post = Post.objects.get(id=post_id)
            like = Like.objects.get(user=request.user, post=post)
            like.delete()
            return Response({"message": "Post unliked."}, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
        except Like.DoesNotExist:
            return Response({"error": "Like not found."}, status=status.HTTP_404_NOT_FOUND)

class FavoritePostView(APIView):
    """
    View to favorite or unfavorite a post.
    """

    def post(self, request, post_id):
        """
        Favorite a post.
        """
        try:
            post = Post.objects.get(id=post_id)
            post.favorites.add(request.user)
            return Response({"message": "Post favorited."}, status=status.HTTP_201_CREATED)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, post_id):
        """
        Unfavorite a post.
        """
        try:
            post = Post.objects.get(id=post_id)
            post.favorites.remove(request.user)
            return Response({"message": "Post unfavorited."}, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)