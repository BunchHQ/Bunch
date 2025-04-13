from typing import override

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UserSerializerTest(APITestCase):
    def __generate_token_pair(self, email: str, password: str) -> tuple[str, str]:
        data = {
            "email": email,
            "password": password,
        }
        url = reverse("token-obtain-pair")
        response = self.client.post(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            f"Getting token pair for user {email} failed!",
        )
        self.assertNotEqual(
            response.json().get("access", None),
            None,
            "response does not contain `access` or None",
        )
        self.assertNotEqual(
            response.json().get("refresh", None),
            None,
            "response does not contain `refresh` or None",
        )

        data = response.json()
        return data["access"], data["refresh"]

    @override
    def setUp(self) -> None:
        # create a root user
        self.root_user = User.objects.create_superuser(
            username="root",
            email="root@bunch.io",
            password="testpassword",
            first_name="Root",
            last_name="R",
        )
        self.root_access_token, self.root_refresh_token = self.__generate_token_pair(
            "root@bunch.io", "testpassword"
        )

        # create a normal user
        self.normal_user = User.objects.create_user(
            username="normal",
            email="normal@bunch.io",
            password="testpassword",
            first_name="Normal",
            last_name="User",
        )
        self.normal_access_token, self.normal_refresh_token = (
            self.__generate_token_pair("normal@bunch.io", "testpassword")
        )

    def test_create_user_no_auth_401(self):
        data = {
            "username": "test",
            "email": "test@bunch.io",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
        }
        url = reverse("user-list")

        response = self.client.post(path=url, data=data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(User.objects.count(), 2)

    def test_create_user_with_normal_auth_403(self):
        data = {
            "username": "test",
            "email": "test@bunch.io",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
        }
        headers = {"Authorization": f"Bearer {self.normal_access_token}"}
        url = reverse("user-list")

        response = self.client.post(path=url, data=data, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), 2)

    def test_create_user_with_root_auth_201(self):
        data = {
            "username": "test",
            "email": "test@bunch.io",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
        }
        headers = {"Authorization": f"Bearer {self.root_access_token}"}
        url = reverse("user-list")

        response = self.client.post(path=url, data=data, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_list_users_no_auth_401(self):
        url = reverse("user-list")

        response = self.client.get(path=url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(User.objects.count(), 2)

    def test_list_users_normal_auth_200(self):
        headers = {"Authorization": f"Bearer {self.normal_access_token}"}
        url = reverse("user-list")

        response = self.client.get(path=url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(len(response.json()["results"]), 2)

    def test_list_users_root_auth_200(self):
        headers = {"Authorization": f"Bearer {self.root_access_token}"}
        url = reverse("user-list")

        response = self.client.get(path=url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(len(response.json()["results"]), 2)

    def test_generate_access_token_using_refresh_token(self):
        url = reverse("token-refresh")
        data = {
            "refresh": self.normal_refresh_token,
        }

        response = self.client.post(path=url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 2)
        self.assertIn("access", response.json())
        self.assertEqual(len(response.json().keys()), 1)
