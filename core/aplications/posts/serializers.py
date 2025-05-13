from rest_framework.serializers import ModelSerializer
from rest_framework.pagination import CursorPagination
from .models import Post, Comment, Like, Favorite, Tags

class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SocialMediaCursorPagination(CursorPagination):
    page_size = 10
    ordering = "-created_at"  # Ordena por fecha de creación descendente
    cursor_query_param = "cursor"  # Parámetro que usará el frontend
