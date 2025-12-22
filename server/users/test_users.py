import logging
from typing import override
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from users.models import (
    ColorChoices,
    ThemePreferenceChoices,
    User,
)

logger = logging.getLogger(__name__)


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
        cls.other_token = "other_token"

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

        cls.other_user = User.objects.create_user(
            username="other_id",
            email="other@example.com",
            password="otherpass",
            first_name="other",
            last_name="User",
        )

        # Patch SupabaseJWTAuthentication.authenticate
        def mock_authenticate(self, request):
            token = (
                request.META.get("HTTP_AUTHORIZATION", "")
                .replace("Bearer ", "")
                .strip()
            )

            logger.debug(f"Mock JWT Auth token={token}")
            user_map = {
                cls.root_token: cls.root_user,
                cls.user_token: cls.user,
                cls.other_token: cls.other_user,
            }

            if token not in user_map:
                logger.warning(f"Mock JWT Auth token={token} not found")
                return (None, None)
            return (user_map[token], None)

        # patch SupabaseAuthMiddleware
        def mock_auth_middleware(self, request):
            if request.user.is_authenticated:
                return self.get_response(request)

            token = (
                request.META.get("HTTP_AUTHORIZATION", "")
                .replace("Bearer ", "")
                .strip()
            )

            logger.debug(f"Mock Auth Middleware token={token}")
            user_map = {
                cls.root_token: cls.root_user,
                cls.user_token: cls.user,
                cls.other_token: cls.other_user,
            }
            if token not in user_map:
                logger.warning(f"Mock Auth Middleware token={token} not found")
                request.user = AnonymousUser()
                return self.get_response(request)

            request.user = user_map[token]
            return self.get_response(request)

        def mock_session_middleware(self, request):
            if request.user.is_authenticated:
                request.supabase = None
            else:
                logger.warning(
                    f"Mock Session Middleware user={request.user} not authenticated"
                )
                request.supabase = None

        cls.auth_patch = patch(
            "orchard.authentication.SupabaseJWTAuthentication.authenticate",
            new=mock_authenticate,
        )
        cls.auth_middleware_patch = patch(
            "orchard.middleware.SupabaseAuthMiddleware.__call__",
            new=mock_auth_middleware,
        )
        cls.session_middleware_patch = patch(
            "orchard.middleware.SupabaseSessionMiddleware.process_request",
            new=mock_session_middleware,
        )

        logger.info("Mocking SupabaseJWTAuthentication.authenticate")
        cls.auth_patch.start()
        logger.info("Mocking SupabaseAuthMiddleware.__call__")
        cls.auth_middleware_patch.start()
        logger.info("Mocking SupabaseSessionMiddleware.process_request")
        cls.session_middleware_patch.start()

    @classmethod
    def tearDownClass(cls):
        cls.auth_patch.stop()
        cls.auth_middleware_patch.stop()
        cls.session_middleware_patch.stop()
        super().tearDownClass()

    def authenticate_user(self, token: str):
        """Helper method to authenticate with mock token"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

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

        response = self.client.post(self.user_list_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), users_before)

    def test_create_user_with_auth_non_root(self):
        self.authenticate_user(self.user_token)
        users_before = User.objects.count()

        response = self.client.post(self.user_list_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), users_before)

    def test_create_user_with_auth_root(self):
        self.authenticate_user(self.root_token)
        users_before = User.objects.count()

        response = self.client.post(self.user_list_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), users_before + 1)

        user = User.objects.get(email=self.user_data["email"])
        self.assertEqual(user.first_name, self.user_data["first_name"])
        self.assertEqual(user.last_name, self.user_data["last_name"])
        self.assertIn(user.color, ColorChoices.values)
        self.assertEqual(
            user.theme_preference,
            ThemePreferenceChoices.SYSTEM,
        )

    def test_list_users_no_auth(self):
        self.client.credentials()
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_with_auth(self):
        self.authenticate_user(self.user_token)
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data.get("results", response.data)
        self.assertGreaterEqual(len(results), 1)

    def test_user_can_get_self_info(self):
        self.authenticate_user(self.user_token)
        response = self.client.get(self.user_me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user = response.data
        self.assertEqual(user["email"], self.user.email)
        self.assertEqual(user["first_name"], self.user.first_name)
        self.assertEqual(user["last_name"], self.user.last_name)
        self.assertEqual(user["username"], self.user.username)
        self.assertEqual(user["color"], self.user.color)

    def test_list_users_normal_auth_200(self):
        self.authenticate_user(self.user_token)
        response = self.client.get(self.user_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(len(response.json()["results"]), 3)

    def test_list_users_root_auth_200(self):
        self.authenticate_user(self.root_token)
        response = self.client.get(self.user_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(len(response.json()["results"]), 3)
