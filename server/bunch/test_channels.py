import os
from typing import override
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from bunch.models import (
    Bunch,
    Channel,
    ChannelTypes,
    Member,
    RoleChoices,
)
from users.models import User


class ChannelsTest(APITestCase):
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
            first_name="Other",
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
                cls.other_token: cls.other_user,
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

    def authenticate_user(self, user_type="test"):
        """Helper method to authenticate with mock token"""
        token_map = {
            "test": self.user_token,
            "root": self.root_token,
            "other": self.other_token,
        }
        token = token_map[user_type]
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

    @override
    def setUp(self):
        self.owner = self.user
        self.root_user = self.root_user
        self.other_user = self.other_user

        self.bunch = Bunch.objects.create(
            name="Test Bunch", owner=self.owner
        )
        # admin member
        Member.objects.filter(
            bunch=self.bunch, user=self.root_user
        ).delete()
        self.admin_member = Member.objects.create(
            bunch=self.bunch,
            user=self.root_user,
            role=RoleChoices.ADMIN,
        )
        # regular member
        Member.objects.filter(
            bunch=self.bunch, user=self.other_user
        ).delete()
        self.member = Member.objects.create(
            bunch=self.bunch,
            user=self.other_user,
            role=RoleChoices.MEMBER,
        )

        self.channels_url = (
            f"/api/v1/bunch/{self.bunch.id}/channels/"
        )

    def test_create_channel_with_owner_auth(self):
        """Test creating a channel with owner authentication"""
        self.authenticate_user(user_type="test")
        channel_data = {
            "name": "Test Channel",
            "type": ChannelTypes.TEXT,
            "description": "Test Description",
            "is_private": False,
            "position": 1,
        }
        response = self.client.post(
            self.channels_url, channel_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Channel creation should succeed",
        )
        channel = Channel.objects.get(
            bunch=self.bunch, name="Test Channel"
        )
        self.assertEqual(
            channel.type,
            ChannelTypes.TEXT,
            "Channel type should be set",
        )
        # TODO: position should be defaulted to 0

    def test_create_channel_with_admin_auth(self):
        """Test creating a channel with admin authentication"""
        self.authenticate_user(user_type="root")
        channel_data = {
            "name": "Admin Channel",
            "type": ChannelTypes.TEXT,
            "description": "Admin Description",
            "is_private": False,
            "position": 1,
        }
        response = self.client.post(
            self.channels_url, channel_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Admin should be able to create channels",
        )
        self.assertTrue(
            Channel.objects.filter(
                bunch=self.bunch, name="Admin Channel"
            ).exists(),
            "Channel should be created",
        )

    def test_create_channel_with_member_auth_fail(self):
        """Test that members cannot create channels"""
        self.authenticate_user(user_type="other")
        channel_data = {
            "name": "Member Channel",
            "type": ChannelTypes.TEXT,
            "description": "Member Description",
            "is_private": False,
            "position": 1,
        }
        response = self.client.post(
            self.channels_url, channel_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular members should not be able to create channels",
        )
        self.assertFalse(
            Channel.objects.filter(
                bunch=self.bunch, name="Member Channel"
            ).exists(),
            "Channel should not be created",
        )

    def test_list_channels_with_member_auth(self):
        """Test listing channels with member authentication"""
        # Create some channels first
        Channel.objects.create(
            bunch=self.bunch,
            name="Channel 1",
            type=ChannelTypes.TEXT,
            position=1,
        )
        Channel.objects.create(
            bunch=self.bunch,
            name="Channel 2",
            type=ChannelTypes.TEXT,
            position=2,
        )

        self.authenticate_user(user_type="other")
        response = self.client.get(self.channels_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Member should be able to list channels",
        )
        self.assertEqual(
            response.data.get("count"),
            2,
            "Should return all channels",
        )
        self.assertEqual(
            len(response.data.get("results")),
            2,
            "Should return all channels",
        )
