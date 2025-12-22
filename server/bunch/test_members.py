import logging
from typing import override

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from bunch.models import Bunch, Member, RoleChoices
from bunch.test_common import OTHER_TOKEN, ROOT_TOKEN, USER_TOKEN, get_mocks
from users.models import User

logger = logging.getLogger(__name__)


class MembersTest(APITestCase):
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

        # URL for member operations
        self.members_url = f"/api/v1/bunch/{self.bunch.id}/members/"

    def test_add_member_with_owner(self):
        """Test adding a member with owner authentication"""
        self.authenticate_user(self.user_token)
        self.assertFalse(
            Member.objects.filter(
                bunch=self.bunch, user=self.other_user
            ).exists(),
            "Member should not exist before test",
        )

        response = self.client.post(
            self.members_url,
            {
                "user": self.other_user.id,
                "nickname": "TestNick",
                "role": RoleChoices.MEMBER,
            },
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Member creation should succeed",
        )
        member = Member.objects.get(bunch=self.bunch, user=self.other_user)
        self.assertEqual(
            member.nickname,
            "TestNick",
            "Member nickname should be set",
        )

    def test_add_member_with_member_auth_403(self):
        """Test adding a member with member authentication"""
        self.authenticate_user(self.other_token)
        response = self.client.post(
            self.members_url,
            {
                "user": self.other_user.id,
                "nickname": "TestNick",
            },
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Non-owner should not be able to add members",
        )

    def test_update_member_role_with_member_auth_403(self):
        """Test updating member role with member authentication"""
        member = Member.objects.create(
            bunch=self.bunch,
            user=self.other_user,
            role=RoleChoices.MEMBER,
        )

        self.authenticate_user(self.other_token)
        # Use DRF's URL pattern for detail actions
        update_role_url = f"{self.members_url}{member.id}/update_role/"
        response = self.client.post(
            update_role_url, {"role": RoleChoices.ADMIN}
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Non-owner should not be able to update roles",
        )

    def test_update_member_role_with_owner_auth_200(self):
        """Test updating member role with owner authentication"""
        member = Member.objects.create(
            bunch=self.bunch,
            user=self.other_user,
            role=RoleChoices.MEMBER,
        )

        self.authenticate_user(self.user_token)
        # Use DRF's URL pattern for detail actions
        update_role_url = f"{self.members_url}{member.id}/update_role/"
        response = self.client.post(
            update_role_url, {"role": RoleChoices.ADMIN}
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Role update should succeed",
        )
        member.refresh_from_db()
        self.assertEqual(
            member.role,
            RoleChoices.ADMIN,
            "Member role should be updated",
        )
