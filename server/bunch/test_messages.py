from typing import override

from rest_framework import status
from rest_framework.test import APITestCase

from bunch.models import (
    Bunch,
    Channel,
    Member,
    Message,
    RoleChoices,
)
from users.models import User


class MessagesTest(APITestCase):
    def setupBunch1(self) -> None:
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="testpass123",
            first_name="Owner",
            last_name="User",
        )
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
        )
        self.member = User.objects.create_user(
            username="member",
            email="member@example.com",
            password="testpass123",
            first_name="Member",
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
            bunch=self.bunch1, user=self.admin
        ).delete()
        self.admin_member_1 = Member.objects.create(
            bunch=self.bunch1,
            user=self.admin,
            role=RoleChoices.ADMIN,
        )
        # regular member
        Member.objects.filter(
            bunch=self.bunch1, user=self.member
        ).delete()
        self.member_member_1 = Member.objects.create(
            bunch=self.bunch1,
            user=self.member,
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

        self.member_2 = User.objects.create_user(
            username="member2",
            email="member2@example.com",
            password="testpass123",
            first_name="Member2",
            last_name="User",
        )

        # owner member was already created with bunch
        self.owner_member_2 = Member.objects.get(
            bunch=self.bunch2,
            user=self.owner,
            role=RoleChoices.OWNER,
        )

        # regular member
        Member.objects.filter(
            bunch=self.bunch2, user=self.member
        ).delete()
        self.member_member_2 = Member.objects.create(
            bunch=self.bunch2,
            user=self.member_2,
            role=RoleChoices.MEMBER,
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

        self.send_message_url_1 = (
            f"/api/v1/bunch/{self.bunch1.id}/channels/{self.channel_general_1.id}/send_message/"
            ""
        )
        self.messages_list_url_1 = (
            f"/api/v1/bunch/{self.bunch1.id}/messages/"
        )

        self.send_message_url_2 = (
            f"/api/v1/bunch/{self.bunch2.id}/channels/{self.channel_general_2.id}/send_message/"
            ""
        )
        self.messages_list_url_2 = (
            f"/api/v1/bunch/{self.bunch2.id}/messages/"
        )

    def test_send_message_with_owner_auth(self):
        """Test sending a message with owner authentication"""
        self.client.force_authenticate(user=self.owner)
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
        self.client.force_authenticate(user=self.admin)
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
        self.client.force_authenticate(user=self.member)
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

        self.client.force_authenticate(user=self.member)
        response = self.client.get(self.messages_list_url_1)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "List request should succeed",
        )

        if "results" in response.data:
            self.assertTrue(
                len(response.data["results"]) >= 1,
                "Paginated response should contain at least one channel",
            )
        else:
            self.assertTrue(
                len(response.data) >= 1,
                "Response should contain at least one channel",
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
        """Test sending a message with to another bunch without membership"""
        self.client.force_authenticate(user=self.member)
        message_data = {"content": "Test Message"}

        # try sending a message in 2nd server
        # while being logged in member who is not in the 2nd server
        response = self.client.post(
            self.send_message_url_2, message_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Message creation should fail",
        )
