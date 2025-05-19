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
    Member,
    Message,
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


class MessagesTest(APITestCase):
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

    def setupBunch1(self) -> None:
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

        self.bunch1 = Bunch.objects.create(
            name="Test Bunch #1", owner=self.owner
        )

        # owner member was already created with bunch
        self.owner_member_1 = Member.objects.get(
            bunch=self.bunch1,
            user=self.owner,
            role=RoleChoices.OWNER,
        )
        # admin member
        Member.objects.filter(
            bunch=self.bunch1, user=self.root_user
        ).delete()
        self.admin_member_1 = Member.objects.create(
            bunch=self.bunch1,
            user=self.root_user,
            role=RoleChoices.ADMIN,
        )
        # regular member
        Member.objects.filter(
            bunch=self.bunch1, user=self.other_user
        ).delete()
        self.member_member_1 = Member.objects.create(
            bunch=self.bunch1,
            user=self.other_user,
            role=RoleChoices.MEMBER,
        )

        self.channel_general_1 = Channel.objects.create(
            bunch=self.bunch1,
            name="General",
            type="text",
        )
        self.channel_other_1 = Channel.objects.create(
            bunch=self.bunch1,
            name="Other",
            type="text",
        )

    def setupBunch2(self) -> None:
        self.bunch2 = Bunch.objects.create(
            name="Test Bunch #2", owner=self.owner
        )

        # owner member was already created with bunch
        self.owner_member_2 = Member.objects.get(
            bunch=self.bunch2,
            user=self.owner,
            role=RoleChoices.OWNER,
        )

        self.channel_general_2 = Channel.objects.create(
            bunch=self.bunch2,
            name="General",
            type="text",
        )
        self.channel_other_2 = Channel.objects.create(
            bunch=self.bunch2,
            name="Other",
            type="text",
        )

    @override
    def setUp(self):
        self.setupBunch1()
        self.setupBunch2()

        self.send_message_url_1 = f"/api/v1/bunch/{self.bunch1.id}/channels/{self.channel_general_1.id}/send_message/"
        self.messages_list_url_1 = (
            f"/api/v1/bunch/{self.bunch1.id}/messages/"
        )

        self.send_message_url_2 = f"/api/v1/bunch/{self.bunch2.id}/channels/{self.channel_general_2.id}/send_message/"
        self.messages_list_url_2 = (
            f"/api/v1/bunch/{self.bunch2.id}/messages/"
        )

    def test_send_message_with_owner_auth(self):
        """Test sending a message with owner authentication"""
        self.authenticate_user(user_type="test")
        message_data = {"content": "Test Message"}

        response = self.client.post(
            self.send_message_url_1, message_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Message creation should succeed",
        )

        message: Message = Message.objects.get(
            channel=self.channel_general_1,
            content="Test Message",
        )
        self.assertEqual(
            message.author,
            self.owner_member_1,
            "Message Author Must be the owner",
        )

    def test_send_message_with_admin_auth(self):
        """Test sending a message with admin authentication"""
        self.authenticate_user(user_type="root")
        message_data = {"content": "Test Message"}

        response = self.client.post(
            self.send_message_url_1, message_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Message creation should succeed",
        )

        message: Message = Message.objects.get(
            channel=self.channel_general_1,
            content="Test Message",
        )
        self.assertEqual(
            message.author,
            self.admin_member_1,
            "Message Author Must be the admin",
        )

    def test_send_message_with_member_auth(self):
        """Test sending a message with member authentication"""
        self.authenticate_user(user_type="other")
        message_data = {"content": "Test Message"}

        response = self.client.post(
            self.send_message_url_1, message_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Message creation should succeed",
        )

        message: Message = Message.objects.get(
            channel=self.channel_general_1,
            content="Test Message",
        )
        self.assertEqual(
            message.author,
            self.member_member_1,
            "Message Author Must be the member",
        )

    def test_list_messages_with_member_auth(self):
        """Test listing messages with member authentication"""
        Message.objects.create(
            content="Test Message",
            channel=self.channel_general_1,
            author=self.member_member_1,
        )

        self.authenticate_user(user_type="other")
        response = self.client.get(self.messages_list_url_1)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "List request should succeed",
        )

        if "results" in response.data:
            self.assertTrue(
                len(response.data["results"]) >= 1,
                "Paginated response should contain at least one message",
            )
        else:
            self.assertTrue(
                len(response.data) >= 1,
                "Response should contain at least one message",
            )

        message_data = (
            response.data[0]
            if "results" not in response.data
            else response.data["results"][0]
        )
        self.assertEqual(
            message_data["content"], "Test Message"
        )
        self.assertEqual(
            message_data["channel_id"],
            str(self.channel_general_1.id),
        )
        self.assertEqual(
            message_data["author_id"],
            str(self.member_member_1.id),
        )

    def test_send_message_bunch_not_member_fail(
        self,
    ) -> None:
        """Test sending a message to another bunch without membership"""
        self.authenticate_user(user_type="other")
        message_data = {"content": "Test Message"}

        # try sending a message in 2nd server
        # while being logged in as member who is not in the 2nd server
        response = self.client.post(
            self.send_message_url_2, message_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Message creation should fail",
        )
