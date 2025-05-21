import os
from typing import override

import requests
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User

# These should be set in your environment for integration tests
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_USER_ID = os.getenv("CLERK_USER_ID")
CLERK_ROOT_ID = os.getenv("CLERK_ROOT_ID")
CLERK_OTHER_USER_ID = os.getenv("CLERK_OTHER_USER_ID")
CLERK_API_URL = os.getenv(
    "CLERK_API_URL", "https://api.clerk.com/v1"
)
CLERK_JWT_TEMPLATE = os.getenv(
    "CLERK_JWT_TEMPLATE", "Django"
)


class ClerkAuthIntegrationTest(TestCase):
    """Integration tests for Clerk authentication.

    These tests require real Clerk API credentials and will make actual API calls.
    They should be run separately from unit tests, possibly in a CI environment
    with proper credentials set up.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        if not all(
            [
                CLERK_SECRET_KEY,
                CLERK_USER_ID,
                CLERK_ROOT_ID,
                CLERK_OTHER_USER_ID,
            ]
        ):
            raise ValueError(
                "CLERK_SECRET_KEY, CLERK_USER_ID, CLERK_ROOT_ID, CLERK_OTHER_USER_ID "
                "environment variables must be set for integration tests"
            )

        # Create test users that match Clerk user IDs
        cls.user = User.objects.create_user(
            username=CLERK_USER_ID,
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        cls.root_user = User.objects.create_superuser(
            username=CLERK_ROOT_ID,
            email="root@example.com",
            password="testpass123",
            first_name="Root",
            last_name="User",
        )

        cls.other_user = User.objects.create_user(
            username=CLERK_OTHER_USER_ID,
            email="other@example.com",
            password="testpass123",
            first_name="Other",
            last_name="User",
        )

        cls.client = APIClient()
        cls.session_tokens = {}

    def get_session_token(self, user_id):
        """Get a real session token from Clerk"""
        if user_id in self.session_tokens:
            return self.session_tokens[user_id]

        # Create a new session
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
        self.session_tokens[user_id] = token
        return token

    def authenticate_user(self, user_type="test"):
        """Authenticate with real Clerk token"""
        user_id = {
            "test": CLERK_USER_ID,
            "root": CLERK_ROOT_ID,
            "other": CLERK_OTHER_USER_ID,
        }[user_type]
        token = self.get_session_token(user_id)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

    def test_authenticate_with_real_token(self):
        """Test authentication with a real Clerk token"""
        self.authenticate_user(user_type="test")
        response = self.client.get("/api/v1/user/me/")
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            response.data["username"], CLERK_USER_ID
        )

    def test_authenticate_with_invalid_token(self):
        """Test authentication with an invalid token"""
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer invalid_token"
        )
        response = self.client.get("/api/v1/user/me/")
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )

    def test_authenticate_with_expired_token(self):
        """Test authentication with an expired token"""
        # Create a token and wait for it to expire
        self.authenticate_user(user_type="test")
        import time

        time.sleep(61)  # Wait for token to expire

        response = self.client.get("/api/v1/user/me/")
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )

    def test_authenticate_with_different_user_types(self):
        """Test authentication with different user types"""
        # Test regular user
        self.authenticate_user(user_type="test")
        response = self.client.get("/api/v1/user/me/")
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            response.data["username"], CLERK_USER_ID
        )

        # Test root user
        self.authenticate_user(user_type="root")
        response = self.client.get("/api/v1/user/me/")
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            response.data["username"], CLERK_ROOT_ID
        )

        # Test other user
        self.authenticate_user(user_type="other")
        response = self.client.get("/api/v1/user/me/")
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            response.data["username"], CLERK_OTHER_USER_ID
        )
