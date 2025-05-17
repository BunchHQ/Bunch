from typing import override

from rest_framework import status
from rest_framework.test import APITestCase

from bunch.models import Bunch, Member, RoleChoices
from users.models import User


class MembersTest(APITestCase):
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

        self.bunch = Bunch.objects.create(
            name="Test Bunch", owner=self.owner
        )

        # URL for member operations
        self.members_url = (
            f"/api/v1/bunch/{self.bunch.id}/members/"
        )

    def test_add_member_with_owner(self):
        """Test adding a member with owner authentication"""
        self.client.force_authenticate(user=self.owner)
        self.assertFalse(
            Member.objects.filter(
                bunch=self.bunch, user=self.member
            ).exists(),
            "Member should not exist before test",
        )

        response = self.client.post(
            self.members_url,
            {
                "user": self.member.id,
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
            bunch=self.bunch, user=self.member
        )
        self.assertEqual(
            member.nickname,
            "TestNick",
            "Member nickname should be set",
        )

    def test_add_member_with_member_auth_403(self):
        """Test adding a member with member authentication"""
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            self.members_url,
            {
                "user": self.member.id,
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
            user=self.member,
            role=RoleChoices.MEMBER,
        )

        self.client.force_authenticate(user=self.member)
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
            user=self.member,
            role=RoleChoices.MEMBER,
        )

        self.client.force_authenticate(user=self.owner)
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
