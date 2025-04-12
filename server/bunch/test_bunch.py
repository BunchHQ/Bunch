import uuid
from typing import override

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Bunch, Channel, Member

User = get_user_model()


class BunchTest(APITestCase):
    @override
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.bunch_data = {
            "name": "Test Bunch",
            "description": "Test Description",
            "is_private": False,
        }
        self.bunch_list_url = "/api/v1/bunch/"

    def test_create_bunch_no_auth(self):
        """Test bunch creation without authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.post(self.bunch_list_url, self.bunch_data)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Unauthenticated request should fail",
        )
        self.assertEqual(Bunch.objects.count(), 0, "Bunch should not be created")

    def test_create_bunch_with_auth(self):
        """Test bunch creation with authentication"""
        response = self.client.post(self.bunch_list_url, self.bunch_data)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Bunch creation should succeed",
        )
        self.assertEqual(Bunch.objects.count(), 1, "Bunch count should be 1")

        bunch = Bunch.objects.first()
        self.assertEqual(
            bunch.owner, self.user, "Bunch owner should be the authenticated user"
        )
        member = Member.objects.first()
        self.assertEqual(member.role, "owner", "First member should be owner")

    def test_list_bunches_no_auth(self):
        """Test listing bunches without authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.bunch_list_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Unauthenticated request should fail",
        )

    def test_list_bunches_with_auth(self):
        """Test listing bunches with authentication"""
        bunch = Bunch.objects.create(name="Test Bunch", owner=self.user)
        Member.objects.get_or_create(
            bunch=bunch, user=self.user, defaults={"role": "owner"}
        )

        response = self.client.get(self.bunch_list_url)
        self.assertEqual(
            response.status_code, status.HTTP_200_OK, "List request should succeed"
        )

        # paginated
        if "results" in response.data:
            self.assertTrue(
                len(response.data["results"]) >= 1,
                "Paginated response should contain at least one bunch",
            )
        else:
            self.assertTrue(
                len(response.data) >= 1, "Response should contain at least one bunch"
            )

    def test_join_private_bunch_with_400(self):
        """Test joining private bunch with invalid invite code"""
        bunch = Bunch.objects.create(
            name="Test Bunch", owner=self.user, is_private=True, invite_code="TEST123"
        )

        # remove the owner
        Member.objects.filter(bunch=bunch, user=self.user).delete()
        join_url = f"/api/v1/bunch/{bunch.id}/join/"
        response = self.client.post(join_url, {"invite_code": "WRONG"})

        # debug
        if response.status_code == 404:
            self.fail(
                f"URL {join_url} not found. Check that the join action is properly registered."
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Invalid invite code should fail",
        )
        self.assertFalse(
            Member.objects.filter(bunch=bunch, user=self.user).exists(),
            "User should not be a member",
        )

    def test_join_private_bunch_with_201(self):
        """Test joining private bunch with valid invite code"""
        bunch = Bunch.objects.create(
            name="Test Bunch", owner=self.user, is_private=True, invite_code="TEST123"
        )

        # remove the owner
        Member.objects.filter(bunch=bunch, user=self.user).delete()
        join_url = f"/api/v1/bunch/{bunch.id}/join/"
        response = self.client.post(join_url, {"invite_code": "TEST123"})

        # debug
        if response.status_code == 404:
            self.fail(
                f"URL {join_url} not found. Check that the join action is properly registered."
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Valid invite code should succeed",
        )
        self.assertTrue(
            Member.objects.filter(bunch=bunch, user=self.user).exists(),
            "User should be a member",
        )

    def test_leave_bunch_204(self):
        """Test leaving a bunch"""
        bunch = Bunch.objects.create(name="Test Bunch", owner=self.user)
        Member.objects.create(bunch=bunch, user=self.user, role="member")

        leave_url = f"/api/v1/bunch/{bunch.id}/leave/"
        response = self.client.post(leave_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            "Leave request should succeed",
        )
        self.assertFalse(
            Member.objects.filter(bunch=bunch, user=self.user).exists(),
            "User should not be a member",
        )
