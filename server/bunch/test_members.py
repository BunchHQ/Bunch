import os
import time
from typing import override

import requests
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from bunch.models import Bunch, Member, RoleChoices
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


class MembersTest(APITestCase):
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

        # URL for member operations
        self.members_url = (
            f"/api/v1/bunch/{self.bunch.id}/members/"
        )

    def test_add_member_with_owner(self):
        """Test adding a member with owner authentication"""
        self.authenticate_user(user_type="test")
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
        member = Member.objects.get(
            bunch=self.bunch, user=self.other_user
        )
        self.assertEqual(
            member.nickname,
            "TestNick",
            "Member nickname should be set",
        )

    def test_add_member_with_member_auth_403(self):
        """Test adding a member with member authentication"""
        self.authenticate_user(user_type="other")
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

        self.authenticate_user(user_type="other")
        # Use DRF's URL pattern for detail actions
        update_role_url = (
            f"{self.members_url}{member.id}/update_role/"
        )
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

        self.authenticate_user(user_type="test")
        # Use DRF's URL pattern for detail actions
        update_role_url = (
            f"{self.members_url}{member.id}/update_role/"
        )
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
