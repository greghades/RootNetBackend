from aplications.authentication.models import CustomUser
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Comment, Like, Post, Favorite

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
        self.user_2 = CustomUser.objects.create_user(
            username="testuser2",
            email="testuser2@example.com",
            password="testpassword",
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

    def test_like_post(self):
        # Create a post first
        post = Post.objects.create(
            content="This is a test post.",
            author=self.user,
        )

        url = reverse("like-service", args=[post.id])
        token_response = self._login_user()

        response = self.client.post(
            url,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)

    def test_unlike_post(self):
        # Create a post and like it first
        post = Post.objects.create(
            content="This is a test post.",
            author=self.user,
        )
        Like.objects.create(
            post=post,
            user=self.user,
        )

        url = reverse("like-service", args=[post.id])
        token_response = self._login_user()

        response = self.client.delete(
            url,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Like.objects.count(), 0)

    def test_already_liked_post(self):
        # Create a post and like it first
        post = Post.objects.create(
            content="This is a test post.",
            author=self.user,
        )
        Like.objects.create(
            post=post,
            user=self.user,
        )

        url = reverse("like-service", args=[post.id])
        token_response = self._login_user()

        response = self.client.post(
            url,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Like.objects.count(), 1)

    def test_favorite_post(self):
        # Create a post first
        post = Post.objects.create(
            content="This is a test post.",
            author=self.user,
        )

        url = reverse("favorite-service")
        token_response = self._login_user()

        data = {
            "post_id": post.id,
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_favorite_post(self):
        # Create a post and favorite it first
        post = Post.objects.create(
            content="This is a test post.",
            author=self.user,
        )
        Favorite.objects.create(
            post=post,
            user=self.user,
        )

        url = reverse("favorite-service")
        token_response = self._login_user()

        data = {
            "post_id": post.id,
        }
        response = self.client.delete(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Favorite.objects.count(), 0)

    def test_already_favorited_post(self):
        # Create a post and favorite it first
        post = Post.objects.create(
            content="This is a test post.",
            author=self.user,
        )
        Favorite.objects.create(
            post=post,
            user=self.user,
        )

        url = reverse("favorite-service")
        token_response = self._login_user()

        data = {
            "post_id": post.id,
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Favorite.objects.count(), 1)

    def test_get_favorites(self):
        # Create a post and favorite it first
        post = Post.objects.create(
            content="This is a test post.",
            author=self.user,
        )
        Favorite.objects.create(
            post=post,
            user=self.user,
        )

        url = reverse("favorite-service")
        token_response = self._login_user()

        response = self.client.get(
            url +"?post_id=" + str(post.id),
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_posts(self):
        # Create a post first
        post = Post.objects.create(
            content="This is a test post.",
            author=self.user,
        )

        url = reverse("post-list")
        token_response = self._login_user()

        response = self.client.get(
            url,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], post.content)

    def test_get_owner_posts(self):
        # Create a post first
        post = Post.objects.create(
            content="This is a test post 1.",
            author=self.user,
        )

        post2 = Post.objects.create(
            content="This is a test post 2.",
            author=self.user,
        )

        post3 = Post.objects.create(
            content="This is a test post 3.",
            author=self.user_2,
        )

        url = reverse("post-owner") + "?user_id=" + str(self.user.id)
        token_response = self._login_user()

        response = self.client.get(
            url,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['content'], post2.content)
        self.assertEqual(response.data[1]['content'], post.content)
        self.assertEqual(response.data[0]['author'], self.user.username)

        url = reverse("post-owner") + "?user_id=" + str(self.user_2.id)
        response = self.client.get(
            url,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data[0]["content"], post3.content)
        self.assertEqual(response.data[0]["author"], self.user_2.username)
