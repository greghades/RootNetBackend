from aplications.authentication.models import CustomUser
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Follow
from aplications.posts.models import Post  # Importa el modelo Post


# Serializer resumido para los posts
class PostSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "content", "created_at", "updated_at","image", "author")  # Incluye los campos que necesites


class FollowSerializer(ModelSerializer):
    class Meta:
        model = Follow
        fields = ("follower", "followed")


class CustomUserProfileSerializer(ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    date_joined = serializers.DateTimeField(format="%d/%m/%Y", read_only=True)
    posts = PostSummarySerializer(source="post_set", many=True, read_only=True)  # Agrega este campo

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "first_name",
            "last_name",
            "profile_photo",
            "date_joined",
            "followers_count",
            "following_count",
            "posts",  # Incluye el campo posts
        )

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()


class CustomUserSettingsSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        exclude = [
            "id",
            "is_staff",
            "groups",
            "user_permissions",
            "is_superuser",
            "last_login",
            "is_active",
            "password",
            "is_checked",
            "created_at",
            "date_joined",
            "following",
        ]
