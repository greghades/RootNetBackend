from datetime import timedelta
from django.db import models
from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from .models import Comment, Favorite, Like, Post
from .serializers import (
    CommentSerializer,
    FavoriteSerializer,
    PostSerializer,
    SocialMediaCursorPagination,
)


class ListPostsFeedView(APIView):
    """
    Vista para listar todas las publicaciones creadas por el usuario autenticado y por los usuarios que sigue.
    """

    pagination_class = SocialMediaCursorPagination

    @swagger_auto_schema(
        operation_summary="Listar publicaciones",
        operation_description="Lista todas las publicaciones creadas por el usuario autenticado y por los usuarios que sigue. Requiere un token JWT válido.",
        responses={200: PostSerializer(many=True)},
        security=[{"Bearer": []}],
    )
    def get(self, request, *args, **kwargs):
        """
        Devuelve las publicaciones del usuario autenticado y de los usuarios que sigue.
        """
        following_users = request.user.following.all()
        posts = Post.objects.filter(
            models.Q(author=request.user) | models.Q(author__in=following_users)
        ).order_by("-created_at")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListPostsOwnerView(APIView):
    """
    Vista para listar todas las publicaciones.
    """

    pagination_class = SocialMediaCursorPagination

    @swagger_auto_schema(
        operation_summary="Listar todas las publicaciones",
        operation_description="Lista todas las publicaciones del ususario.",
        manual_parameters=[
            openapi.Parameter(
                "user_id",
                openapi.IN_QUERY,
                description="ID del usuario para filtrar las publicaciones",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={200: PostSerializer(many=True)},
        security=[{"Bearer": []}],
    )
    def get(self, request, *args, **kwargs):
        """
        Devuelve todas las publicaciones.
        """
        owner = request.query_params.get("user_id", None)
        if owner is None:
            return Response(
                {"error": "owner parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        posts = Post.objects.filter(author=owner).order_by("-created_at")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreatePostView(CreateAPIView):
    """
    Vista para crear una nueva publicación.
    """

    serializer_class = PostSerializer

    @swagger_auto_schema(
        operation_summary="Crear una publicación",
        operation_description="Crea una nueva publicación. Requiere un token JWT válido.",
        manual_parameters=[
            openapi.Parameter(
                "title",
                openapi.IN_QUERY,
                description="Título de la publicación",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "content",
                openapi.IN_QUERY,
                description="Contenido de la publicación",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "image",
                openapi.IN_QUERY,
                description="Imagen de la publicación (opcional)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "tags",
                openapi.IN_QUERY,
                description="Etiquetas de la publicación (opcional, separadas por comas)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={
            201: PostSerializer,
            400: openapi.Response(description="Solicitud incorrecta"),
        },
        security=[{"Bearer": []}],
    )
    def post(self, request, *args, **kwargs):
        """
        Crea una nueva publicación con los datos proporcionados.
        """
        return super().post(request, *args, **kwargs)


class DeletePostView(APIView):
    """
    Vista para eliminar una publicación por su ID.
    """

    serializer_class = PostSerializer

    @swagger_auto_schema(
        operation_summary="Eliminar una publicación",
        operation_description="Elimina una publicación por su ID. Requiere un token JWT válido.",
        responses={
            204: openapi.Response(description="Publicación eliminada"),
            404: openapi.Response(description="No encontrada"),
        },
        security=[{"Bearer": []}],
    )
    def delete(self, request, post_id, *args, **kwargs):
        """
        Elimina la publicación especificada por su ID.
        """

        try:
            post = Post.objects.get(id=post_id)
            if post.author != request.user:
                return Response(
                    {"error": "You do not have permission to delete this post."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class UpdatePostView(UpdateAPIView):
    """
    Vista para actualizar una publicación existente por su ID.
    """

    serializer_class = PostSerializer

    @swagger_auto_schema(
        operation_summary="Actualizar una publicación",
        operation_description="Actualiza una publicación por su ID. Requiere un token JWT válido.",
        request_body=PostSerializer,
        responses={
            200: PostSerializer,
            404: openapi.Response(description="No encontrada"),
        },
        security=[{"Bearer": []}],
    )
    def patch(self, request, post_id, *args, **kwargs):
        """
        Actualiza los datos de la publicación especificada.
        """
        try:
            post = Post.objects.get(id=post_id)
            if post.author != request.user:
                return Response(
                    {"error": "You do not have permission to update this post."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Validación de las 24 horas
            if timezone.now() > post.created_at + timedelta(hours=24):
                return Response(
                    {
                        "error": "No se puede actualizar la publicación después de 24 horas de su creación."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = self.get_serializer(post, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class CommentsView(APIView):
    """
    Vista para gestionar los comentarios de las publicaciones.
    """

    @swagger_auto_schema(
        operation_summary="Obtener comentarios de una publicación",
        operation_description="Obtiene todos los comentarios asociados a una publicación específica. Requiere un token JWT válido.",
        manual_parameters=[
            openapi.Parameter(
                "post_id",
                openapi.IN_QUERY,
                description="ID de la publicación para obtener comentarios",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: CommentSerializer(many=True),
            400: openapi.Response(
                description="Solicitud incorrecta",
                examples={"application/json": {"error": "post_id is required."}},
            ),
            404: openapi.Response(
                description="No encontrada",
                examples={"application/json": {"error": "Post not found."}},
            ),
        },
        security=[{"Bearer": []}],
    )
    def get(self, request, *args, **kwargs):
        """
        Devuelve los comentarios de una publicación específica.
        """
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
        operation_summary="Crear un comentario",
        operation_description="Crea un nuevo comentario para una publicación específica. Requiere un token JWT válido.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["post_id", "content"],
            properties={
                "post_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID de la publicación a comentar",
                ),
                "content": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Contenido del comentario"
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Comentario creado",
                examples={
                    "application/json": {"message": "Comment created successfully"}
                },
            ),
            400: openapi.Response(
                description="Solicitud incorrecta",
                examples={
                    "application/json": {"error": "post_id and content are required."}
                },
            ),
            404: openapi.Response(
                description="No encontrada",
                examples={"application/json": {"message": "Post not found"}},
            ),
        },
        security=[{"Bearer": []}],
    )
    def post(self, request, *args, **kwargs):
        """
        Crea un comentario en una publicación específica.
        """
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
        operation_summary="Actualizar un comentario",
        operation_description="Actualiza el contenido de un comentario específico. Requiere un token JWT válido.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["comment_id", "content"],
            properties={
                "comment_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID del comentario a actualizar",
                ),
                "content": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Nuevo contenido del comentario",
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Comentario actualizado",
                examples={
                    "application/json": {"message": "Comment updated successfully"}
                },
            ),
            400: openapi.Response(
                description="Solicitud incorrecta",
                examples={
                    "application/json": {
                        "error": "comment_id and content are required."
                    }
                },
            ),
            404: openapi.Response(
                description="No encontrado",
                examples={"application/json": {"message": "Comment not found"}},
            ),
        },
        security=[{"Bearer": []}],
    )
    def patch(self, request, *args, **kwargs):
        """
        Actualiza el contenido de un comentario existente.
        """
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
        operation_summary="Eliminar un comentario",
        operation_description="Elimina un comentario específico. Requiere un token JWT válido.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["comment_id"],
            properties={
                "comment_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID del comentario a eliminar",
                ),
            },
        ),
        responses={
            204: openapi.Response(
                description="Comentario eliminado",
                examples={
                    "application/json": {"message": "Comment deleted successfully"}
                },
            ),
            400: openapi.Response(
                description="Solicitud incorrecta",
                examples={"application/json": {"error": "comment_id is required."}},
            ),
            404: openapi.Response(
                description="No encontrado",
                examples={"application/json": {"message": "Comment not found"}},
            ),
        },
        security=[{"Bearer": []}],
    )
    def delete(self, request, *args, **kwargs):
        """
        Elimina un comentario específico.
        """
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
    Vista para dar o quitar 'me gusta' a una publicación.
    """

    @swagger_auto_schema(
        operation_summary="Dar me gusta a una publicación",
        operation_description="Da me gusta a una publicación por su ID. Requiere un token JWT válido.",
        manual_parameters=[
            openapi.Parameter(
                "post_id",
                openapi.IN_PATH,
                description="ID de la publicación a dar me gusta",
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
        """
        Da me gusta a una publicación específica.
        """
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
        operation_summary="Quitar me gusta a una publicación",
        operation_description="Quita el me gusta de una publicación por su ID. Requiere un token JWT válido.",
        manual_parameters=[
            openapi.Parameter(
                "post_id",
                openapi.IN_PATH,
                description="ID de la publicación para quitar me gusta",
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
        """
        Quita el me gusta de una publicación específica.
        """
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
    """
    Vista para gestionar publicaciones favoritas del usuario.
    """

    @swagger_auto_schema(
        operation_summary="Verificar si una publicación es favorita",
        operation_description="Verifica si una publicación es favorita para el usuario autenticado. Requiere un token JWT válido.",
        manual_parameters=[
            openapi.Parameter(
                "post_id",
                openapi.IN_QUERY,
                description="ID de la publicación a verificar",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(description="Estado de favorito"),
            400: openapi.Response(description="post_id es requerido"),
            404: openapi.Response(description="Publicación no encontrada"),
        },
        security=[{"Bearer": []}],
    )
    def get(self, request):
        """
        Verifica si una publicación es favorita para el usuario autenticado.
        """
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
        operation_summary="Agregar una publicación a favoritos",
        operation_description="Agrega una publicación a favoritos por su ID. Requiere un token JWT válido.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["post_id"],
            properties={
                "post_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID de la publicación a agregar a favoritos",
                ),
            },
        ),
        responses={
            201: openapi.Response(description="Publicación agregada a favoritos"),
            400: openapi.Response(description="Ya es favorita o post_id es requerido"),
            404: openapi.Response(description="Publicación no encontrada"),
        },
        security=[{"Bearer": []}],
    )
    def post(self, request):
        """
        Agrega una publicación a favoritos del usuario autenticado.
        """
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
        operation_summary="Quitar una publicación de favoritos",
        operation_description="Quita una publicación de favoritos por su ID. Requiere un token JWT válido.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["post_id"],
            properties={
                "post_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID de la publicación a quitar de favoritos",
                ),
            },
        ),
        responses={
            204: openapi.Response(description="Publicación eliminada de favoritos"),
            400: openapi.Response(description="post_id es requerido"),
            404: openapi.Response(description="Publicación o favorito no encontrado"),
        },
        security=[{"Bearer": []}],
    )
    def delete(self, request):
        """
        Quita una publicación de favoritos del usuario autenticado.
        """
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
