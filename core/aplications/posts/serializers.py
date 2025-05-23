from aplications.authentication.models import CustomUser
from rest_framework import serializers
from rest_framework.pagination import CursorPagination

from .models import Comment, Favorite, Like, Post, Tags


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username", queryset=CustomUser.objects.all(), required=False
    )
    created_at = serializers.DateTimeField(format="%d/%m/%Y/%H/%M", read_only=True)
    updated_at = serializers.DateTimeField(format="%d/%m/%Y/%H/%M", read_only=True)
    image = serializers.ImageField(required=False, allow_null=True, use_url=True)

    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def validate_author(self, value):
        request = self.context.get("request")
        print("Request user:", request.user)
        if request and request.user != value:
            raise serializers.ValidationError(
                "El usuario debe ser el usuario autenticado."
            )
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if request:
            validated_data["author"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("author", None)
        return super().update(instance, validated_data)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username", queryset=CustomUser.objects.all(), required=False
    )
    created_at = serializers.DateTimeField(format="%d/%m/%Y", read_only=True)
    updated_at = serializers.DateTimeField(format="%d/%m/%Y", read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def validate_author(self, value):
        request = self.context.get("request")
        if request and request.user != value:
            raise serializers.ValidationError(
                "El usuario debe ser el usuario autenticado."
            )
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if request:
            validated_data["author"] = request.user
        return super().create(validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=CustomUser.objects.all(), required=False
    )
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    created_at = serializers.DateTimeField(format="%d/%m/%Y", read_only=True)
    updated_at = serializers.DateTimeField(format="%d/%m/%Y", read_only=True)

    class Meta:
        model = Favorite
        exclude = ("id",)
        read_only_fields = ["created_at", "updated_at"]

    def validate_user(self, value):
        request = self.context.get("request")
        if request and request.user != value:
            raise serializers.ValidationError(
                "El usuario debe ser el usuario autenticado."
            )
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if request:
            validated_data["user"] = request.user
        return super().create(validated_data)


class SocialMediaCursorPagination(CursorPagination):
    page_size = 10
    ordering = "-created_at"  # Ordena por fecha de creación descendente
    cursor_query_param = "cursor"  # Parámetro que usará el frontend
