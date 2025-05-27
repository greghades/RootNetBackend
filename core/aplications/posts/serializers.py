from aplications.authentication.models import CustomUser
from rest_framework import serializers
from rest_framework.pagination import CursorPagination

from .models import Comment, Favorite, Like, Post, Tags


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username", queryset=CustomUser.objects.all()
    )
    tag_names = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    author_first_name = serializers.SerializerMethodField()
    author_last_name = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%d/%m/%y/%H/%M", read_only=True)
    updated_at = serializers.DateTimeField(format="%d/%m/%y/%H/%M", read_only=True)
    tags_names = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "author_first_name",
            "author_last_name",
            "content",
            "image",
            "created_at",
            "updated_at",
            "comments_count",
            "favorites_count",
            "likes_count",
            "tag_names",
            "tags_names",
        ]
        extra_fields = ["tag_names"]
        read_only_fields = ["created_at", "updated_at"]

    def get_author_first_name(self, obj):
        return obj.author.first_name

    def get_author_last_name(self, obj):
        return obj.author.last_name

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_favorites_count(self, obj):
        return obj.favorites.count()

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_tags_names(self, obj):
        return [tag.name for tag in obj.tag.all()]

    def create(self, validated_data):
        tags_data = validated_data.pop("tag_names", [])
        post = super().create(validated_data)
        for tag_name in tags_data:
            tag_obj, created = Tags.objects.get_or_create(name=tag_name)
            post.tag.add(tag_obj)
        return post

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
