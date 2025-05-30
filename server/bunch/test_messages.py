import os
import time
from typing import override
from unittest.mock import patch

import requests
from bunch.models import Bunch, Channel, Member, Message, RoleChoices
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from users.models import User

load_dotenv()


class MessagesTest(APITestCase):
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

    def setupBunch1(self) -> None:
        self.owner = self.user
        self.root_user = self.root_user
        self.other_user = self.other_user

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

    def test_list_messages_filtered_by_channel(self):
        """Test that messages are properly filtered by channel when channel parameter is provided"""
        # Create messages in different channels of the same bunch
        message_general = Message.objects.create(
            content="Message in General",
            channel=self.channel_general_1,
            author=self.member_member_1,
        )

        message_other = Message.objects.create(
            content="Message in Other",
            channel=self.channel_other_1,
            author=self.member_member_1,
        )

        self.authenticate_user(user_type="other")

        # Test filtering by general channel
        response = self.client.get(
            f"{self.messages_list_url_1}?channel={self.channel_general_1.id}"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "List request should succeed",
        )

        messages = (
            response.data["results"]
            if "results" in response.data
            else response.data
        )

        # Should only return messages from general channel
        self.assertEqual(
            len(messages), 1,
            "Should only return 1 message from general channel"
        )
        self.assertEqual(
            messages[0]["content"], "Message in General"
        )
        self.assertEqual(
            messages[0]["channel_id"], str(self.channel_general_1.id)
        )

        # Test filtering by other channel
        response = self.client.get(
            f"{self.messages_list_url_1}?channel={self.channel_other_1.id}"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "List request should succeed",
        )

        messages = (
            response.data["results"]
            if "results" in response.data
            else response.data
        )

        # Should only return messages from other channel
        self.assertEqual(
            len(messages), 1,
            "Should only return 1 message from other channel"
        )
        self.assertEqual(
            messages[0]["content"], "Message in Other"
        )
        self.assertEqual(
            messages[0]["channel_id"], str(self.channel_other_1.id)
        )

        # Test without channel filter - should return all messages from the bunch
        response = self.client.get(self.messages_list_url_1)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "List request should succeed",
        )

        messages = (
            response.data["results"]
            if "results" in response.data
            else response.data
        )

        # Should return all messages when no channel filter is applied
        self.assertEqual(
            len(messages), 2,
            "Should return all messages when no channel filter is applied"
        )
