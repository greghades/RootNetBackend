from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Follow
from .serializers import FollowSerializer, CustomUserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.


class ProfileView(generics.GenericAPIView):
    @swagger_auto_schema(
        operation_summary="Get user profile",
        operation_description="Retrieves the authenticated user's profile. Requires a valid JWT token.",
        responses={
            200: CustomUserSerializer,
            401: openapi.Response(description="Unauthorized"),
        },
        security=[{"Bearer": []}],
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Update user profile",
        operation_description="Updates the authenticated user's profile. Requires a valid JWT token.",
        request_body=CustomUserSerializer,
        responses={
            200: CustomUserSerializer,
            400: openapi.Response(description="Bad Request"),
        },
        security=[{"Bearer": []}],
    )

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowUserView(generics.GenericAPIView):

    def post(self, request, *args, **kwargs) -> Response:

        follow_data = {
            "follower": request.user.id,
            "followed": request.data.get("followed", None)
        }

        serializer = FollowSerializer(data=follow_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnfollowUserView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs) -> Response:
        try:
        
            follow = Follow.objects.get(
                follower=request.user.id,
                followed=request.data.get("followed", None)
            )
            follow.delete()
            return Response({"message": "Unfollowed successfully"}, status=status.HTTP_200_OK)
        except Follow.DoesNotExist as e:
            
            return Response({"error": "Follow relationship does not exist"}, status=status.HTTP_400_BAD_REQUEST)
