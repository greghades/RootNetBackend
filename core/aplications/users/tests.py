from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from rest_framework import status
from aplications.authentication.models import CustomUser
# Create your tests here.

class UserViewTestCase(APITestCase):
    def setUp(self):
        # Create a user and authenticate
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(
            username="user1",
            email="user1@example.com", password="password123"
        )
        self.user2 = CustomUser.objects.create_user(
            username="user2",
            email="user2@example.com", password="password123"
        )
        self.user3 = CustomUser.objects.create_user(
            username="user3",
            email="user3@example.com", password="password123"
        )
        self.client.force_authenticate(user=self.user1)

    def test_get_user_profile(self):
        url = reverse("profile")
        response = self.client.get(url)
        

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user1.username)
        self.assertEqual(response.data["email"], self.user1.email)

    def test_get_other_user_profile(self):

        url = reverse("follow") 
        data = {"followed": self.user2.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {"followed": self.user3.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse("user-profile", args=[self.user2.username])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user2.username)

        print(response.data)

    def test_follow_user(self):
        url = reverse("follow")
        data = {"followed": self.user2.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_multiple_follow_user(self):
        url = reverse("follow")
        data = {"followed": self.user2.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {"followed": self.user3.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.logout()

        self.client.force_authenticate(user=self.user2)
        data = {"followed": self.user1.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.logout()
        self.client.force_authenticate(user=self.user1)
        url = reverse("profile")
        response = self.client.get(url)

    def test_update_user_profile(self):
        url = reverse("profile")
        data = {
            "username": "new_username",
            "email": "new_email@example.com"
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "new_username")
        self.assertEqual(response.data["email"], "new_email@example.com")

    def test_follow_user_already_followed(self):

        url = reverse("follow")
        data = {"followed": self.user2.id}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_follow_user_not_found(self):
        url = reverse("follow")
        data = {"followed": 9999}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_follow_user_unauthenticated(self):
        self.client.logout()
        url = reverse("follow")
        data = {"followed": self.user2.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unfollow_user(self):

        url_follow = reverse("follow")
        data = {"followed": self.user2.id}

        response = self.client.post(url_follow, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url_unfollow = reverse("unfollow")
        data = {"followed": self.user2.id}
        response = self.client.post(url_unfollow, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Unfollowed successfully")

    def test_unfollow_user_not_following(self):
        url = reverse("unfollow")
        data = {"followed": self.user2.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfollow_user_not_found(self):
        url = reverse("unfollow")
        data = {"followed": 9999}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfollow_user_unauthenticated(self):
        self.client.logout()
        url = reverse("unfollow")
        data = {"followed": self.user2.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
