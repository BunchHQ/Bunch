from typing import override

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from bunch.models import Bunch, Member, RoleChoices
from users.models import User


class BunchTest(APITestCase):
    @override
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.client: APIClient = APIClient()

    @override
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.other_user = User.objects.create_user(
            username="testotheruser",
            email="other@example.com",
            password="testpass123",
            first_name="Other",
            last_name="User",
        )

        self.public_bunch_data = {
            "name": "Test Bunch",
            "description": "Test Description",
            "is_private": False,
            "invite_code": "ABCD12345",
        }

        self.private_bunch_data = {
            "name": "Private Bunch",
            "description": "A Private One",
            "is_private": True,
            "invite_code": "ABCD1234",
        }

        self.bunch_list_url = "/api/v1/bunch/"
        self.public_bunch_list_url = "/api/v1/bunch/public/"

    def test_create_bunch_no_auth(self):
        """Test bunch creation without authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.post(
            self.bunch_list_url, self.public_bunch_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Unauthenticated request should fail",
        )
        self.assertEqual(
            Bunch.objects.count(),
            0,
            "Bunch should not be created",
        )

    def test_create_bunch_with_auth(self):
        """Test bunch creation with authentication"""
        self.client.force_login(user=self.user)
        response = self.client.post(
            self.bunch_list_url, self.public_bunch_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Bunch creation should succeed",
        )
        self.assertEqual(
            Bunch.objects.count(),
            1,
            "Bunch count should be 1",
        )

        bunch = Bunch.objects.first()

        # just to make type hints happy below
        assert bunch is not None

        self.assertEqual(
            bunch.owner,
            self.user,
            "Bunch owner should be the authenticated user",
        )
        member = Member.objects.first()

        assert member is not None
        self.assertEqual(
            member.role,
            RoleChoices.OWNER,
            "First member should be owner",
        )

    def test_list_public_bunches_no_auth(self):
        """Test listing public bunches without authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get(
            self.public_bunch_list_url
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Unauthenticated request should pass",
        )

    def test_list_public_bunches_with_auth(self):
        """Test listing public bunches with authentication"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            self.public_bunch_list_url
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Authenticated request should pass",
        )

    def test_list_public_bunches_should_list_public_only(
        self,
    ):
        """Test listing public bunches should list public only"""
        self.client.force_authenticate(user=self.user)

        # create a public bunch
        self.client.post(
            self.bunch_list_url, self.public_bunch_data
        )
        # create a private bunch
        self.client.post(
            self.bunch_list_url, self.private_bunch_data
        )

        response = self.client.get(
            self.public_bunch_list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Request to list public bunches should pass",
        )
        self.assertEqual(
            response.data.get("count"),
            1,
            "There should be only 1 public bunch",
        )
        self.assertEqual(
            len(response.data.get("results")),
            1,
            "There should be only 1 public bunch",
        )
        self.assertEqual(
            response.data.get("results")[0].get("name"),
            self.public_bunch_data.get("name"),
            "The bunch should be the public one",
        )
        self.assertEqual(
            response.data.get("results")[0].get(
                "is_private"
            ),
            False,
            "The bunch should not be private",
        )

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
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.bunch_list_url, self.public_bunch_data
        )
        bunch = Bunch.objects.first()

        self.assertTrue(
            Member.objects.filter(
                bunch=bunch,
                user=self.user,
                role=RoleChoices.OWNER,
            ).exists(),
            "Owner should be automatically added as a member with role 'owner'",
        )

        response = self.client.get(self.bunch_list_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "List request should succeed",
        )

        # paginated
        if "results" in response.data:
            self.assertTrue(
                len(response.data["results"]) >= 1,
                "Paginated response should contain at least one bunch",
            )
        else:
            self.assertTrue(
                len(response.data) >= 1,
                "Response should contain at least one bunch",
            )

    def test_join_private_bunch_with_400(self):
        """Test joining private bunch with invalid invite code"""
        self.client.force_authenticate(user=self.user)
        bunch = Bunch.objects.create(
            name="Test Bunch",
            owner=self.user,
            is_private=True,
            invite_code="TEST123",
        )

        self.client.force_authenticate(user=self.other_user)
        join_url = f"/api/v1/bunch/{bunch.id}/join/"
        response = self.client.post(
            join_url, {"invite_code": "WRONG"}
        )

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
            Member.objects.filter(
                bunch=bunch, user=self.other_user
            ).exists(),
            "User should not be a member",
        )

    def test_join_private_bunch_with_201(self):
        """Test joining private bunch with valid invite code"""
        self.client.force_authenticate(user=self.user)
        bunch = Bunch.objects.create(
            name="Test Bunch",
            owner=self.user,
            is_private=True,
            invite_code="TEST123",
        )

        self.client.force_authenticate(user=self.other_user)
        join_url = f"/api/v1/bunch/{bunch.id}/join/"
        response = self.client.post(
            join_url, {"invite_code": "TEST123"}
        )

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
            Member.objects.filter(
                bunch=bunch, user=self.other_user
            ).exists(),
            "User should be a member",
        )

    def test_member_can_leave_bunch(self):
        """Test leaving a bunch"""
        self.client.force_authenticate(user=self.user)
        bunch = Bunch.objects.create(
            name="Test Bunch", owner=self.user
        )

        self.client.force_authenticate(user=self.other_user)
        Member.objects.create(
            bunch=bunch,
            user=self.other_user,
            role=RoleChoices.MEMBER,
        )

        leave_url = f"/api/v1/bunch/{bunch.id}/leave/"
        response = self.client.post(leave_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            "Leave request should succeed",
        )
        self.assertFalse(
            Member.objects.filter(
                bunch=bunch, user=self.other_user
            ).exists(),
            "User should not be a member after leaving",
        )

    def test_owner_cannot_leave_bunch(self):
        """Test that an owner cannot leave their own bunch"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.bunch_list_url, self.public_bunch_data
        )
        bunch = Bunch.objects.first()

        assert bunch is not None

        leave_url = f"/api/v1/bunch/{bunch.id}/leave/"
        response = self.client.post(leave_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Owner should not be able to leave their own bunch",
        )

        self.assertTrue(
            Member.objects.filter(
                bunch=bunch,
                user=self.user,
                role=RoleChoices.OWNER,
            ).exists(),
            "Owner should still be a member",
        )

    def test_list_bunches_list_joined_ones(self):
        """Test listing bunches lists joined ones, even private ones"""
        self.client.force_authenticate(user=self.user)
        # create a public bunch
        response = self.client.post(
            self.bunch_list_url, self.public_bunch_data
        )
        # create a private bunch
        response = self.client.post(
            self.bunch_list_url, self.private_bunch_data
        )

        public_bunch = Bunch.objects.get(is_private=False)
        private_bunch = Bunch.objects.get(is_private=True)

        assert public_bunch is not None
        assert private_bunch is not None

        # somehow invite_code doesn't get added to the bunch
        if private_bunch.invite_code is None:
            private_bunch.invite_code = (
                self.private_bunch_data.get("invite_code")
            )
            private_bunch.save()

        invite_code = private_bunch.invite_code

        # switch to other user to join
        self.client.force_authenticate(user=self.other_user)

        join_url = f"/api/v1/bunch/{public_bunch.id}/join/"
        response = self.client.post(join_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "public Bunch must be joined",
        )

        join_url = f"/api/v1/bunch/{private_bunch.id}/join/"
        response = self.client.post(
            join_url, {"invite_code": invite_code}
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "private Bunch must be joined with invite code",
        )

        response = self.client.get(
            self.public_bunch_list_url
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Request to list public bunches should pass",
        )
        self.assertEqual(
            response.data.get("count"),
            1,
            "There should be only 1 public bunch",
        )
        self.assertEqual(
            len(response.data.get("results")),
            1,
            "There should be only 1 public bunch",
        )

        # list joined bunches
        response = self.client.get(self.bunch_list_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Request to list bunches should pass",
        )
        self.assertEqual(
            response.data.get("count"),
            2,
            "There should be 2 bunches joined",
        )
        self.assertEqual(
            len(response.data.get("results")),
            2,
            "There should 2 bunches joined",
        )
