from typing import override

from rest_framework import status
from rest_framework.test import APITestCase

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
    def setUp(self):
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

        self.bunch = Bunch.objects.create(
            name="Test Bunch", owner=self.owner
        )
        # admin member
        Member.objects.filter(
            bunch=self.bunch, user=self.admin
        ).delete()
        Member.objects.create(
            bunch=self.bunch,
            user=self.admin,
            role=RoleChoices.ADMIN,
        )
        # regular member
        Member.objects.filter(
            bunch=self.bunch, user=self.member
        ).delete()
        Member.objects.create(
            bunch=self.bunch,
            user=self.member,
            role=RoleChoices.MEMBER,
        )

        self.channels_url = (
            f"/api/v1/bunch/{self.bunch.id}/channels/"
        )

    def test_create_channel_with_owner_auth(self):
        """Test creating a channel with owner authentication"""
        self.client.force_authenticate(user=self.owner)
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
        # admins can create channels
        self.client.force_authenticate(user=self.admin)
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
            "Admins should be able to create channels",
        )

    def test_create_channel_with_member_auth_fail(self):
        """Test creating a channel with member authentication fails"""
        # members can't create channels
        self.client.force_authenticate(user=self.member)
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
            status.HTTP_403_FORBIDDEN,
            "Members shouldn't be able to create channels",
        )

    def test_list_channels_with_member_auth(self):
        """Test listing channels with member authentication"""
        Channel.objects.create(
            bunch=self.bunch,
            name="Test Channel",
            type=ChannelTypes.TEXT,
            position=1,
        )

        self.client.force_authenticate(user=self.member)
        response = self.client.get(self.channels_url)
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

        channel_data = (
            response.data[0]
            if "results" not in response.data
            else response.data["results"][0]
        )
        self.assertEqual(
            channel_data["name"], "Test Channel"
        )
        self.assertEqual(
            channel_data["type"], ChannelTypes.TEXT
        )
