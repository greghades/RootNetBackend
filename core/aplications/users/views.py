from aplications.posts.serializers import PostSerializer, SocialMediaCursorPagination
from django.shortcuts import get_object_or_404, render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Follow
from .serializers import (
    CustomUser,
    CustomUserProfileSerializer,
    CustomUserSettingsSerializer,
    FollowSerializer,
)

# Create your views here.


class ProfileSettingsView(generics.GenericAPIView):
    """
    Vista para obtener y actualizar el perfil del usuario autenticado.
    """

    @swagger_auto_schema(
        operation_summary="Obtener perfil de usuario",
        operation_description="Recupera el perfil del usuario autenticado. Requiere un token JWT válido.",
        responses={
            200: CustomUserSettingsSerializer,
            401: openapi.Response(description="Unauthorized"),
        },
        security=[{"Bearer": []}],
    )
    def get(self, request, *args, **kwargs):
        """
        Devuelve los datos del perfil del usuario autenticado.
        """
        user = request.user
        serializer = CustomUserSettingsSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Actualizar perfil de usuario",
        operation_description="Actualiza el perfil del usuario autenticado. Requiere un token JWT válido.",
        request_body=CustomUserSettingsSerializer,
        responses={
            200: CustomUserSettingsSerializer,
            400: openapi.Response(description="Bad Request"),
        },
        security=[{"Bearer": []}],
    )
    def put(self, request, *args, **kwargs):
        """
        Actualiza los datos del perfil del usuario autenticado.
        """
        user = request.user
        serializer = CustomUserSettingsSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.GenericAPIView):
    """
    Vista para obtener el perfil de un usuario con posts paginados (scroll infinito).
    """

    serializer_class = CustomUserProfileSerializer
    pagination_class = (
        SocialMediaCursorPagination  # Usa el paginador de scroll infinito
    )

    def get(self, request, username, *args, **kwargs):
        if not username:
            return Response(
                {"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        user = get_object_or_404(CustomUser, username=username)

        # Paginar los posts del usuario
        posts_qs = user.post_set.all().order_by("-created_at")
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(posts_qs, request)
        posts_serializer = PostSerializer(page, many=True)

        # Serializar el usuario y reemplazar el campo 'posts' por los paginados
        user_serializer = CustomUserProfileSerializer(user)
        data = user_serializer.data
        data["posts"] = posts_serializer.data

        return paginator.get_paginated_response(data)


class FollowUserView(generics.GenericAPIView):
    """
    Vista para seguir a otro usuario.
    """

    @swagger_auto_schema(
        operation_summary="Seguir a un usuario",
        operation_description="El usuario autenticado sigue a otro usuario. Requiere un token JWT válido.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["followed"],
            properties={
                "followed": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID del usuario a seguir"
                ),
            },
        ),
        responses={
            201: FollowSerializer,
            400: openapi.Response(description="Bad Request"),
        },
        security=[{"Bearer": []}],
    )
    def post(self, request, *args, **kwargs) -> Response:
        """
        Permite al usuario autenticado seguir a otro usuario.
        """
        follow_data = {
            "follower": request.user.id,
            "followed": request.data.get("followed", None),
        }
        serializer = FollowSerializer(data=follow_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UnfollowUserView(generics.GenericAPIView):
    """
    Vista para dejar de seguir a un usuario.
    """

    @swagger_auto_schema(
        operation_summary="Dejar de seguir a un usuario",
        operation_description="El usuario autenticado deja de seguir a otro usuario. Requiere un token JWT válido.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["followed"],
            properties={
                "followed": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID del usuario a dejar de seguir",
                ),
            },
        ),
        responses={
            200: openapi.Response(description="Unfollowed successfully"),
            400: openapi.Response(description="Bad Request"),
        },
        security=[{"Bearer": []}],
    )
    def post(self, request, *args, **kwargs) -> Response:
        """
        Permite al usuario autenticado dejar de seguir a otro usuario.
        """
        try:
            follow = Follow.objects.get(
                follower=request.user.id, followed=request.data.get("followed", None)
            )
            follow.delete()
            return Response(
                {"message": "Unfollowed successfully"}, status=status.HTTP_200_OK
            )
        except Follow.DoesNotExist:
            return Response(
                {"error": "The relationship does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
