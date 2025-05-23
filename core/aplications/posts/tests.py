from aplications.authentication.models import CustomUser
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Comment, Like, Post

# Create your tests here.


class PostTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "email": "testuser@example.com",
            "password": "testpassword",
        }
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email=self.user_data["email"],
            password=self.user_data["password"],
        )

    def _login_user(self):
        # Helper method to log in the user and get the access token
        url = reverse("login")

        data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        }
        response = self.client.post(url, data, format="json")

        return response

    def test_create_post_with_jwt(self):
        url = reverse("post-create")
        token_response = self._login_user()

        data = {
            "content": "This is a test post.",
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)

    def test_add_comment_to_post(self):
        # Create a post first
        post = Post.objects.create(
            content="This is a test post.",
            author=self.user,
        )

        url = reverse("comment-service")
        token_response = self._login_user()

        data = {
            "content": "This is a test comment.",
            "post_id": post.id,
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)

    def test_get_comments_for_post(self):
        # Create a post and a comment first
        post = Post.objects.create(
            content="This is a test post.",
            author=self.user,
        )
        Comment.objects.create(
            content="This is a test comment.",
            post=post,
            author=self.user,
        )

        url = reverse("comment-service") + f"?post_id={post.id}"
        token_response = self._login_user()

        response = self.client.get(
            url,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_edit_comment(self):
        # Create a post and a comment first
        post = Post.objects.create(
            content="This is a test post.",
            author=self.user,
        )
        comment = Comment.objects.create(
            content="This is a test comment.",
            post=post,
            author=self.user,
        )

        url = reverse("comment-service")
        token_response = self._login_user()

        data = {
            "comment_id": comment.id,
            "content": "This is an edited comment.",
        }
        response = self.client.patch(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.content, "This is an edited comment.")
    
    def test_delete_comment(self):
        # Create a post and a comment first
        post = Post.objects.create(
            content="This is a test post.",
            author=self.user,
        )
        comment = Comment.objects.create(
            content="This is a test comment.",
            post=post,
            author=self.user,
        )

        url = reverse("comment-service")
        token_response = self._login_user()

        data = {
            "comment_id": comment.id,
        }
        response = self.client.delete(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)
