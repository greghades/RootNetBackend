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
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        #self.client.force_authenticate(user=self.user)

    # def test_create_post(self):

    #     url = reverse("post-create")
    #     data = {
    #         "title": "Test Post",
    #         "content": "This is a test post.",
    #         "author": self.user.id,
    #     }
    #     response = self.client.post(url, data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Post.objects.count(), 1)
    #     post = Post.objects.get()
    #     self.assertEqual(post.title, "Test Post")
    #     self.assertEqual(post.content, "This is a test post.")
    #     self.assertEqual(post.author, self.user)

    # def test_pagination(self):
    #     # Crea más datos para probar paginación
    #     for i in range(25):  # Más que el page_size (20)
    #         Post.objects.create(
    #             title=f"Post {i}",
    #             content=f"This is post number {i}.",
    #             author=self.user,
    #         )

    #     url = reverse("post-list")
    #     response = self.client.get(url)

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data["results"]), 10)  # page_size
    #     self.assertIsNotNone(response.data["next"])  # Hay más páginas

    # def test_update_post(self):
    #     post = Post.objects.create(
    #         title="Old Title",
    #         content="Old content.",
    #         author=self.user,
    #     )
    #     url = reverse("post-update", args=[post.id])
    #     data = {
    #         "title": "Updated Title",
    #         "content": "Updated content.",
    #         "author": self.user.id,
    #     }

    #     response = self.client.put(url, data, format="json")

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     post.refresh_from_db()
    #     self.assertEqual(post.title, "Updated Title")
    #     self.assertEqual(post.content, "Updated content.")

    # def test_delete_post(self):
    #     post = Post.objects.create(
    #         title="Post to delete",
    #         content="This post will be deleted.",
    #         author=self.user,
    #     )
    #     url = reverse("post-delete", args=[post.id])
    #     response = self.client.delete(url)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertEqual(Post.objects.count(), 0)

    def test_obtain_jwt_token(self):
        url = reverse("token_obtain_pair")
        data = {
            "email": "testuser@example.com",
            "password": "testpassword",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

    def test_create_post_with_jwt(self):
        url = reverse("post-list")
        token_url = reverse("token_obtain_pair")
        token_response = self.client.post(
            token_url,
            {"email": "testuser@example.com", "password": "testpassword"},
            format="json",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {token_response.data["access"]}'
        )
        data = {
            "title": "Test Post",
            "content": "This is a test post.",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
