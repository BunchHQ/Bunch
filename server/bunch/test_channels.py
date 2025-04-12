import uuid
from typing import override

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Bunch, Channel, Member

User = get_user_model()


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
        self.member = User.objects.create_user(
            username="member",
            email="member@example.com",
            password="testpass123",
            first_name="Member",
            last_name="User",
        )
        self.client = APIClient()

        self.bunch = Bunch.objects.create(name="Test Bunch", owner=self.owner)
        # owner member
        Member.objects.create(bunch=self.bunch, user=self.owner, role="owner")
        # regular member
        Member.objects.filter(bunch=self.bunch, user=self.member).delete()
        Member.objects.create(bunch=self.bunch, user=self.member, role="member")

        self.channels_url = f"/api/v1/bunch/{self.bunch.id}/channels/"

    def test_create_channel_with_owner_auth_201(self):
        """Test creating a channel with owner authentication"""
        self.client.force_authenticate(user=self.owner)
        channel_data = {
            "name": "Test Channel",
            "type": "text",
            "description": "Test Description",
            "is_private": False,
            "position": 1,
        }
        response = self.client.post(self.channels_url, channel_data)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Channel creation should succeed",
        )
        channel = Channel.objects.get(bunch=self.bunch, name="Test Channel")
        self.assertEqual(channel.type, "text", "Channel type should be set")
        # TODO: position should be defaulted to 0

    def test_create_channel_with_member_auth(self):
        """Test creating a channel with member authentication"""
        # members can create channels
        self.client.force_authenticate(user=self.member)
        channel_data = {
            "name": "Test Channel",
            "type": "text",
            "description": "Test Description",
            "is_private": False,
            "position": 1,
        }
        response = self.client.post(self.channels_url, channel_data)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Members should be able to create channels",
        )

    def test_list_channels_with_member_auth_200(self):
        """Test listing channels with member authentication"""
        channel = Channel.objects.create(
            bunch=self.bunch, name="Test Channel", type="text", position=1
        )

        self.client.force_authenticate(user=self.member)
        response = self.client.get(self.channels_url)
        self.assertEqual(
            response.status_code, status.HTTP_200_OK, "List request should succeed"
        )

        if "results" in response.data:
            self.assertTrue(
                len(response.data["results"]) >= 1,
                "Paginated response should contain at least one channel",
            )
        else:
            self.assertTrue(
                len(response.data) >= 1, "Response should contain at least one channel"
            )

        channel_data = (
            response.data[0]
            if "results" not in response.data
            else response.data["results"][0]
        )
        self.assertEqual(channel_data["name"], "Test Channel")
        self.assertEqual(channel_data["type"], "text")
