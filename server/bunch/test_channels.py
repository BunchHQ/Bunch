import os
import time
from typing import override

import requests
from dotenv import load_dotenv
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

load_dotenv()

# Get Clerk configuration from environment variables
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

if not all(
    [
        CLERK_SECRET_KEY,
        CLERK_USER_ID,
        CLERK_ROOT_ID,
        CLERK_OTHER_USER_ID,
    ]
):
    raise ValueError(
        "CLERK_SECRET_KEY, CLERK_USER_ID, CLERK_ROOT_ID, CLERK_OTHER_USER_ID environment variables must be set"
    )


class ChannelsTest(APITestCase):
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

    def authenticate_user(self, user_type="test"):
        """Helper method to authenticate with Clerk token"""
        user_id = {
            "test": CLERK_USER_ID,
            "root": CLERK_ROOT_ID,
            "other": CLERK_OTHER_USER_ID,
        }[user_type]
        token = self.get_session_token(user_id)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

    @override
    def setUp(self):
        self.owner = User.objects.create_user(
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
        self.other_user = User.objects.create_user(
            username=CLERK_OTHER_USER_ID,
            email="other@example.com",
            password="testpass123",
            first_name="Other",
            last_name="User",
        )

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
