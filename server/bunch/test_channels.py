import logging
from typing import override

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from bunch.models import (
    Bunch,
    Channel,
    ChannelTypes,
    Member,
    RoleChoices,
)
from bunch.test_common import OTHER_TOKEN, ROOT_TOKEN, USER_TOKEN, get_mocks
from users.models import User

logger = logging.getLogger(__name__)


class ChannelsTest(APITestCase):
    @override
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.client: APIClient = APIClient()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.root_token = ROOT_TOKEN
        cls.user_token = USER_TOKEN
        cls.other_token = OTHER_TOKEN

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

        auth_patch, auth_middleware_path, session_middleware_patch = get_mocks(
            logger, cls
        )
        cls.auth_patch = auth_patch
        cls.auth_middleware_patch = auth_middleware_path
        cls.session_middleware_patch = session_middleware_patch

        logger.debug("Mocking SupabaseJWTAuthentication.authenticate")
        cls.auth_patch.start()
        logger.debug("Mocking SupabaseAuthMiddleware.__call__")
        cls.auth_middleware_patch.start()
        logger.debug("Mocking SupabaseSessionMiddleware.process_request")
        cls.session_middleware_patch.start()

    @classmethod
    def tearDownClass(cls):
        cls.auth_patch.stop()
        cls.auth_middleware_patch.stop()
        cls.session_middleware_patch.stop()
        super().tearDownClass()

    def authenticate_user(self, token):
        """Helper method to authenticate with mock token"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    @override
    def setUp(self):
        self.owner = self.user
        self.root_user = self.root_user
        self.other_user = self.other_user

        self.bunch = Bunch.objects.create(name="Test Bunch", owner=self.owner)
        # admin member
        Member.objects.filter(bunch=self.bunch, user=self.root_user).delete()
        self.admin_member = Member.objects.create(
            bunch=self.bunch,
            user=self.root_user,
            role=RoleChoices.ADMIN,
        )
        # regular member
        Member.objects.filter(bunch=self.bunch, user=self.other_user).delete()
        self.member = Member.objects.create(
            bunch=self.bunch,
            user=self.other_user,
            role=RoleChoices.MEMBER,
        )

        self.channels_url = f"/api/v1/bunch/{self.bunch.id}/channels/"

    def test_create_channel_with_owner_auth(self):
        """Test creating a channel with owner authentication"""
        self.authenticate_user(self.user_token)
        channel_data = {
            "name": "Test Channel",
            "type": ChannelTypes.TEXT,
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
        self.assertEqual(
            channel.type,
            ChannelTypes.TEXT,
            "Channel type should be set",
        )
        # TODO: position should be defaulted to 0

    def test_create_channel_with_admin_auth(self):
        """Test creating a channel with admin authentication"""
        self.authenticate_user(self.root_token)
        channel_data = {
            "name": "Admin Channel",
            "type": ChannelTypes.TEXT,
            "description": "Admin Description",
            "is_private": False,
            "position": 1,
        }
        response = self.client.post(self.channels_url, channel_data)
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
        self.authenticate_user(self.other_token)
        channel_data = {
            "name": "Member Channel",
            "type": ChannelTypes.TEXT,
            "description": "Member Description",
            "is_private": False,
            "position": 1,
        }
        response = self.client.post(self.channels_url, channel_data)
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

        self.authenticate_user(self.other_token)
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
