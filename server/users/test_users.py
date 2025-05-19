import os
import time
from typing import override

import requests
from django.urls import reverse
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from users.models import (
    ColorChoices,
    ThemePreferenceChoices,
    User,
)

load_dotenv()

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_USER_ID = os.getenv("CLERK_USER_ID")
CLERK_ROOT_ID = os.getenv("CLERK_ROOT_ID")
CLERK_API_URL = os.getenv(
    "CLERK_API_URL", "https://api.clerk.com/v1"
)
CLERK_JWT_TEMPLATE = os.getenv(
    "CLERK_JWT_TEMPLATE", "Django"
)

if not all(
    [
        CLERK_SECRET_KEY,
        CLERK_USER_ID,
        CLERK_ROOT_ID,
    ]
):
    raise ValueError(
        "CLERK_SECRET_KEY, CLERK_USER_ID, CLERK_ROOT_ID environment variables must be set"
    )


class UsersTest(APITestCase):
    @override
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.client: APIClient = APIClient()
        self.session_tokens = {}

    def get_session_token(self, user_id):
        """Get a valid session token from Clerk"""

        # https://clerk.com/docs/testing/overview

        if user_id in self.session_tokens:
            token_data = self.session_tokens[user_id]
            # must beless than 60 seconds old
            if (
                time.time() - token_data["created_at"] < 55
            ):  # 55 seconds to be safe
                return token_data["token"]

        session_response = requests.post(
            f"{CLERK_API_URL}/sessions",
            headers={
                "Authorization": f"Bearer {CLERK_SECRET_KEY}"
            },
            json={"user_id": user_id},
        )
        if session_response.status_code != 200:
            raise Exception(
                f"Failed to create session: {session_response.text}"
            )

        session_id = session_response.json()["id"]

        # Create a session token
        token_response = requests.post(
            f"{CLERK_API_URL}/sessions/{session_id}/tokens/{CLERK_JWT_TEMPLATE}",
            headers={
                "Authorization": f"Bearer {CLERK_SECRET_KEY}"
            },
            json={"expires_in_seconds": 60},
        )
        if token_response.status_code != 200:
            raise Exception(
                f"Failed to create session token: {token_response.text}"
            )

        token = token_response.json()["jwt"]
        self.session_tokens[user_id] = {
            "token": token,
            "created_at": time.time(),
        }
        return token

    def authenticate_user(self, is_root=False):
        """Helper method to authenticate with Clerk session token"""
        user_id = (
            CLERK_ROOT_ID if is_root else CLERK_USER_ID
        )
        token = self.get_session_token(user_id)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

    @override
    def setUp(self):
        # Create test users in the database
        self.user = User.objects.create_user(
            username=CLERK_USER_ID,
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        self.root_user = User.objects.create_superuser(
            username=CLERK_ROOT_ID,
            email="root@example.com",
            password="testpass123",
            first_name="Root",
            last_name="User",
        )

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
        """Test user creation without authentication"""
        self.client.credentials()  # Clear any existing credentials
        users_before = User.objects.count()

        response = self.client.post(
            self.user_list_url, self.user_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Unauthenticated request should fail",
        )
        self.assertEqual(
            User.objects.count(),
            users_before,
            "User should not be created",
        )

    def test_create_user_with_auth_non_root(self):
        """Test user creation with normal user authentication"""
        self.authenticate_user(is_root=False)
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
        self.authenticate_user(is_root=True)
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
        self.client.credentials()  # Clear any existing credentials
        response = self.client.get(self.user_list_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Unauthenticated request should fail",
        )

    def test_list_users_with_auth(self):
        """Test listing users with authentication"""
        self.authenticate_user(is_root=False)
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
        self.authenticate_user(is_root=False)

        response = self.client.get(self.user_me_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Get request should succeed",
        )

        user = response.data
        self.assertEqual(
            user["email"],
            self.user.email,
            "User email should be the same as the user",
        )
        self.assertEqual(
            user["first_name"],
            self.user.first_name,
            "User first name should be the same as the user",
        )
        self.assertEqual(
            user["last_name"],
            self.user.last_name,
            "User last name should be the same as the user",
        )
        self.assertEqual(
            user["username"],
            self.user.username,
            "User username should be the same as the user",
        )
        self.assertEqual(
            user["color"],
            self.user.color,
            "User color should be the same as the user",
        )

    def test_list_users_normal_auth_200(self):
        """Test listing users with normal user authentication"""
        self.authenticate_user(is_root=False)
        response = self.client.get(self.user_list_url)

        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(len(response.json()["results"]), 2)

    def test_list_users_root_auth_200(self):
        """Test listing users with root authentication"""
        self.authenticate_user(is_root=True)
        response = self.client.get(self.user_list_url)

        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(len(response.json()["results"]), 2)
