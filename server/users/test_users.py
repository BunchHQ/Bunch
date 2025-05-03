from typing import override

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

    @override
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        self.other_user = User.objects.create_user(
            username="testotheruser",
            email="other@example.com",
            password="testpass123",
            first_name="Other",
            last_name="User",
        )
        self.root_user = User.objects.create_superuser(
            username="testrootuser",
            email="root@example.com",
            password="testpass123",
            first_name="Root",
            last_name="User",
        )

        self.user_data = {
            "email": "testnew@bunch.io",
            "username": "testnew",
            "first_name": "Test",
            "last_name": "New",
            "password": "newuser@123",
            "status": "Happy Day",
            "bio": "Happy Evening",
            "pronoun": "he/him",
        }

        self.user_list_url = "/api/v1/user/"
        self.user_me_url = "/api/v1/user/me/"

    def test_create_user_no_auth(self):
        """Test user creation without authentication"""
        self.client.force_authenticate(user=None)
        users_before = User.objects.count()

        response = self.client.post(
            self.user_list_url, self.user_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Unauthenticated request should fail",
        )
        self.assertEqual(
            User.objects.count(),
            users_before,
            "User should not be created",
        )

    def test_create_user_with_auth_non_root(self):
        """Test user creation with normal user authentication"""
        self.client.force_login(user=self.user)
        users_before = User.objects.count()

        response = self.client.post(
            self.user_list_url, self.user_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Unauthorized request should fail",
        )
        self.assertEqual(
            User.objects.count(),
            users_before,
            "User should not be created",
        )

    def test_create_user_with_auth_root(self):
        """Test user creation with root authentication"""
        self.client.force_login(user=self.root_user)
        users_before = User.objects.count()

        response = self.client.post(
            self.user_list_url, self.user_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "User creation should succeed",
        )
        self.assertEqual(
            User.objects.count(),
            users_before + 1,
            f"User count should be {users_before + 1}",
        )

        user = User.objects.first()

        # just to make type hints happy below
        assert user is not None

        self.assertEqual(
            user.email,
            self.user_data["email"],
            "User email should be the same as the data",
        )
        self.assertEqual(
            user.first_name,
            self.user_data["first_name"],
            "User first name should be the same as the data",
        )
        self.assertEqual(
            user.last_name,
            self.user_data["last_name"],
            "User last name should be the same as the data",
        )
        self.assertIn(
            user.color,
            ColorChoices.values,
            "User color should be a random color",
        )
        self.assertIn(
            user.theme_preference,
            ThemePreferenceChoices.SYSTEM,
            "User theme_preference should be system",
        )

    def test_list_users_no_auth(self):
        """Test listing users without authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.user_list_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Unauthenticated request should fail",
        )

    def test_list_users_with_auth(self):
        """Test listing users with authentication"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.user_list_url, self.user_data
        )

        response = self.client.get(self.user_list_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "List request should succeed",
        )

        # paginated
        if "results" in response.data:
            self.assertTrue(
                len(response.data["results"]) >= 1,
                "Paginated response should contain at least one user",
            )
        else:
            self.assertTrue(
                len(response.data) >= 1,
                "Response should contain at least one user",
            )

    def test_user_can_get_self_info(self) -> None:
        """Test user can get self info"""
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.user_me_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Get request should succeed",
        )

        user = response.data
        self.assertEqual(
            user["email"],
            self.other_user.email,
            "User email should be the same as the user",
        )
        self.assertEqual(
            user["first_name"],
            self.other_user.first_name,
            "User first name should be the same as the user",
        )
        self.assertEqual(
            user["last_name"],
            self.other_user.last_name,
            "User last name should be the same as the user",
        )
        self.assertEqual(
            user["username"],
            self.other_user.username,
            "User username should be the same as the user",
        )
        self.assertEqual(
            user["color"],
            self.other_user.color,
            "User color should be the same as the user",
        )
