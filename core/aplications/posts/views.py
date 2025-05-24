from django.db import models
from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Favorite, Like, Post
from .serializers import (
    CommentSerializer,
    FavoriteSerializer,
    PostSerializer,
    SocialMediaCursorPagination,
)


class ListPostsView(APIView):

    pagination_class = SocialMediaCursorPagination

    @swagger_auto_schema(
        operation_summary="List posts",
        operation_description="List all posts created by the user and by users they follow. Requires a valid JWT token.",
        responses={200: PostSerializer(many=True)},
        security=[{"Bearer": []}],
    )
    def get(self, request, *args, **kwargs):
        following_users = request.user.following.all()
        posts = Post.objects.filter(
            models.Q(author=request.user) | models.Q(author__in=following_users)
        ).order_by("-created_at")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreatePostView(CreateAPIView):
    serializer_class = PostSerializer

    @swagger_auto_schema(
        operation_summary="Create a new post",
        operation_description="Creates a new post. Requires a valid JWT token.",
        request_body=PostSerializer,
        responses={
            201: PostSerializer,
            400: openapi.Response(description="Bad Request"),
        },
        security=[{"Bearer": []}],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DeletePostView(DestroyAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    @swagger_auto_schema(
        operation_summary="Delete a post",
        operation_description="Delete a post by ID. Requires a valid JWT token.",
        responses={
            204: openapi.Response(description="Post deleted"),
            404: openapi.Response(description="Not Found"),
        },
        security=[{"Bearer": []}],
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class UpdatePostView(UpdateAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    @swagger_auto_schema(
        operation_summary="Update a post",
        operation_description="Update a post by ID. Requires a valid JWT token.",
        request_body=PostSerializer,
        responses={
            200: PostSerializer,
            404: openapi.Response(description="Not Found"),
        },
        security=[{"Bearer": []}],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


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
        security=[{"Bearer": []}],
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

    @swagger_auto_schema(
        operation_summary="Like a post",
        operation_description="Like a post by ID. Requires a valid JWT token.",
        manual_parameters=[
            openapi.Parameter(
                "post_id",
                openapi.IN_PATH,
                description="ID of the post to like",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            201: openapi.Response(description="Post liked"),
            400: openapi.Response(description="Post already liked"),
            404: openapi.Response(description="Post not found"),
        },
        security=[{"Bearer": []}],
    )
    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            like, created = Like.objects.get_or_create(user=request.user, post=post)
            if created:
                return Response(
                    {"message": "Post liked."}, status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"message": "Post already liked."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_summary="Unlike a post",
        operation_description="Unlike a post by ID. Requires a valid JWT token.",
        manual_parameters=[
            openapi.Parameter(
                "post_id",
                openapi.IN_PATH,
                description="ID of the post to unlike",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            204: openapi.Response(description="Post unliked"),
            404: openapi.Response(description="Post or Like not found"),
        },
        security=[{"Bearer": []}],
    )
    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            like = Like.objects.get(user=request.user, post=post)
            like.delete()
            return Response(
                {"message": "Post unliked."}, status=status.HTTP_204_NO_CONTENT
            )
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Like.DoesNotExist:
            return Response(
                {"error": "Like not found."}, status=status.HTTP_404_NOT_FOUND
            )


class FavoritePostView(APIView):

    @swagger_auto_schema(
        operation_summary="Check if a post is favorited",
        operation_description="Check if a post is favorited by the user. Requires a valid JWT token.",
        manual_parameters=[
            openapi.Parameter(
                "post_id",
                openapi.IN_QUERY,
                description="ID of the post to check",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(description="Favorite status"),
            400: openapi.Response(description="post_id is required"),
            404: openapi.Response(description="Post not found"),
        },
        security=[{"Bearer": []}],
    )
    def get(self, request):
        post_id = request.query_params.get("post_id", None)
        if not post_id:
            return Response(
                {"error": "post_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            post = Post.objects.get(id=post_id)
            favorited_posts = Favorite.objects.filter(user=request.user, post=post)
            if not favorited_posts.exists():
                return Response({"is_favorited": False}, status=status.HTTP_200_OK)
            favorites_serializer = FavoriteSerializer(favorited_posts, many=True)
            return Response(
                {"Posts_Favorites": favorites_serializer.data},
                status=status.HTTP_200_OK,
            )
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_summary="Favorite a post",
        operation_description="Favorite a post by ID. Requires a valid JWT token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["post_id"],
            properties={
                "post_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the post to favorite",
                ),
            },
        ),
        responses={
            201: openapi.Response(description="Post favorited"),
            400: openapi.Response(
                description="Post already favorited or post_id is required"
            ),
            404: openapi.Response(description="Post not found"),
        },
        security=[{"Bearer": []}],
    )
    def post(self, request):
        post_id = request.data.get("post_id", None)
        if not post_id:
            return Response(
                {"error": "post_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            post = Post.objects.get(id=post_id)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user, post=post
            )
            if not created:
                return Response(
                    {"message": "Post already favorited."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"message": "Post favorited."}, status=status.HTTP_201_CREATED
            )
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_summary="Unfavorite a post",
        operation_description="Unfavorite a post by ID. Requires a valid JWT token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["post_id"],
            properties={
                "post_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the post to unfavorite",
                ),
            },
        ),
        responses={
            204: openapi.Response(description="Post unfavorited"),
            400: openapi.Response(description="post_id is required"),
            404: openapi.Response(description="Post or Favorite not found"),
        },
        security=[{"Bearer": []}],
    )
    def delete(self, request):
        post_id = request.data.get("post_id", None)
        if not post_id:
            return Response(
                {"error": "post_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            post = Post.objects.get(id=post_id)
            favorite = Favorite.objects.get(user=request.user, post=post)
            favorite.delete()
            return Response(
                {"message": "Post unfavorited."}, status=status.HTTP_204_NO_CONTENT
            )
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Favorite.DoesNotExist:
            return Response(
                {"error": "Favorite not found."}, status=status.HTTP_404_NOT_FOUND
            )
