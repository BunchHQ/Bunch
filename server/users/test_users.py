import os
from typing import override
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from users.models import (
    ColorChoices,
    ThemePreferenceChoices,
    User,
)


class UsersTest(APITestCase):
    @override
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.client: APIClient = APIClient()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.root_token = "root_token"
        cls.user_token = "user_token"
        cls.third_token = "third_token"

        # Create test users
        cls.root_user = User.objects.create_superuser(
            username="root_id",
            email="root@example.com",
            password="rootpass",
            first_name="Root",
            last_name="User",
        )

        cls.user = User.objects.create_user(
            username="user_id",
            email="user@example.com",
            password="userpass",
            first_name="Test",
            last_name="User",
        )

        cls.third_user = User.objects.create_user(
            username="third_id",
            email="third@example.com",
            password="thirdpass",
            first_name="Third",
            last_name="User",
        )

        # Patch ClerkJWTAuthentication.authenticate
        def mock_authenticate(self, request):
            token = request.headers.get(
                "Authorization", ""
            ).replace("Bearer ", "")
            user_map = {
                cls.root_token: cls.root_user,
                cls.user_token: cls.user,
                cls.third_token: cls.third_user,
            }
            if token not in user_map:
                return (None, None)
            return (user_map[token], None)

        cls.auth_patch = patch(
            "orchard.middleware.ClerkJWTAuthentication.authenticate",
            new=mock_authenticate,
        )
        cls.auth_patch.start()

    @classmethod
    def tearDownClass(cls):
        cls.auth_patch.stop()
        super().tearDownClass()

    def authenticate_user(self, token: str):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

    @override
    def setUp(self):
        self.user_data = {
            "email": "testnew@bunch.io",
            "username": "testnewbunch",
            "first_name": "Test",
            "last_name": "New",
            "password": "newuser@123",
            "status": "Happy Day",
            "bio": "Happy Evening",
            "pronoun": "he/him",
        }

        self.user_list_url = reverse("users:user-list")
        self.user_me_url = "/api/v1/user/me/"

    def test_create_user_no_auth(self):
        self.client.credentials()
        users_before = User.objects.count()

        response = self.client.post(
            self.user_list_url, self.user_data
        )
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(User.objects.count(), users_before)

    def test_create_user_with_auth_non_root(self):
        self.authenticate_user(self.user_token)
        users_before = User.objects.count()

        response = self.client.post(
            self.user_list_url, self.user_data
        )
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(User.objects.count(), users_before)

    def test_create_user_with_auth_root(self):
        self.authenticate_user(self.root_token)
        users_before = User.objects.count()

        response = self.client.post(
            self.user_list_url, self.user_data
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )
        self.assertEqual(
            User.objects.count(), users_before + 1
        )

        user = User.objects.get(
            email=self.user_data["email"]
        )
        self.assertEqual(
            user.first_name, self.user_data["first_name"]
        )
        self.assertEqual(
            user.last_name, self.user_data["last_name"]
        )
        self.assertIn(user.color, ColorChoices.values)
        self.assertEqual(
            user.theme_preference,
            ThemePreferenceChoices.SYSTEM,
        )

    def test_list_users_no_auth(self):
        self.client.credentials()
        response = self.client.get(self.user_list_url)
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )

    def test_list_users_with_auth(self):
        self.authenticate_user(self.user_token)
        response = self.client.get(self.user_list_url)
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )

        results = response.data.get(
            "results", response.data
        )
        self.assertGreaterEqual(len(results), 1)

    def test_user_can_get_self_info(self):
        self.authenticate_user(self.user_token)
        response = self.client.get(self.user_me_url)
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )

        user = response.data
        self.assertEqual(user["email"], self.user.email)
        self.assertEqual(
            user["first_name"], self.user.first_name
        )
        self.assertEqual(
            user["last_name"], self.user.last_name
        )
        self.assertEqual(
            user["username"], self.user.username
        )
        self.assertEqual(user["color"], self.user.color)

    def test_list_users_normal_auth_200(self):
        self.authenticate_user(self.user_token)
        response = self.client.get(self.user_list_url)

        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(len(response.json()["results"]), 3)

    def test_list_users_root_auth_200(self):
        self.authenticate_user(self.root_token)
        response = self.client.get(self.user_list_url)

        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(len(response.json()["results"]), 3)
