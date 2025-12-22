import logging
from typing import override

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from bunch.models import Bunch, Member, RoleChoices
from bunch.test_common import OTHER_TOKEN, ROOT_TOKEN, USER_TOKEN, get_mocks
from users.models import User

logger = logging.getLogger(__name__)


class BunchTest(APITestCase):
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
        self.user = self.user
        self.root_user = self.root_user
        self.other_user = self.other_user

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
        self.client.credentials()  # Clear any existing credentials
        response = self.client.post(self.bunch_list_url, self.public_bunch_data)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Unauthenticated request should fail",
        )
        self.assertEqual(
            Bunch.objects.count(),
            0,
            "Bunch should not be created",
        )

    def test_create_bunch_with_auth(self):
        """Test bunch creation with authentication"""
        self.authenticate_user(self.user_token)
        response = self.client.post(self.bunch_list_url, self.public_bunch_data)
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
        self.client.credentials()
        response = self.client.get(self.public_bunch_list_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Unauthenticated request should pass",
        )

    def test_list_public_bunches_with_auth(self):
        """Test listing public bunches with authentication"""
        self.authenticate_user(self.user_token)
        response = self.client.get(self.public_bunch_list_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Authenticated request should pass",
        )

    def test_list_public_bunches_should_list_public_only(
        self,
    ):
        """Test listing public bunches should list public only"""
        self.authenticate_user(self.user_token)

        # create a public bunch
        self.client.post(self.bunch_list_url, self.public_bunch_data)
        # create a private bunch
        self.client.post(self.bunch_list_url, self.private_bunch_data)

        response = self.client.get(self.public_bunch_list_url)

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
            response.data.get("results")[0].get("is_private"),
            False,
            "The bunch should not be private",
        )

    def test_list_bunches_no_auth(self):
        """Test listing bunches without authentication"""
        self.client.credentials()  # Clear any existing credentials
        response = self.client.get(self.bunch_list_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Unauthenticated request should fail",
        )

    def test_list_bunches_with_auth(self):
        """Test listing bunches with authentication"""
        self.authenticate_user(self.user_token)
        response = self.client.post(self.bunch_list_url, self.public_bunch_data)
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
        self.authenticate_user(self.user_token)
        bunch = Bunch.objects.create(
            name="Test Bunch",
            owner=self.user,
            is_private=True,
            invite_code="TEST123",
        )

        self.authenticate_user(self.other_token)  # Switch to other user
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
            Member.objects.filter(bunch=bunch, user=self.other_user).exists(),
            "Member should not be created with invalid invite code",
        )

    def test_join_private_bunch_with_201(self):
        """Test joining private bunch with valid invite code"""
        self.authenticate_user(self.user_token)
        bunch = Bunch.objects.create(
            name="Test Bunch",
            owner=self.user,
            is_private=True,
            invite_code="TEST123",
        )

        self.authenticate_user(self.other_token)  # Switch to other user
        join_url = f"/api/v1/bunch/{bunch.id}/join/"
        response = self.client.post(join_url, {"invite_code": "TEST123"})

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Valid invite code should succeed",
        )
        self.assertTrue(
            Member.objects.filter(bunch=bunch, user=self.other_user).exists(),
            "Member should be created with valid invite code",
        )

    def test_member_can_leave_bunch(self):
        """Test member can leave bunch"""
        self.authenticate_user(self.user_token)
        bunch = Bunch.objects.create(
            name="Test Bunch",
            owner=self.user,
            is_private=True,
            invite_code="TEST123",
        )

        self.authenticate_user(self.other_token)  # Switch to other user
        join_url = f"/api/v1/bunch/{bunch.id}/join/"
        self.client.post(join_url, {"invite_code": "TEST123"})

        leave_url = f"/api/v1/bunch/{bunch.id}/leave/"
        response = self.client.post(leave_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Member should be able to leave",
        )
        self.assertFalse(
            Member.objects.filter(bunch=bunch, user=self.other_user).exists(),
            "Member should be removed",
        )

    def test_owner_cannot_leave_bunch(self):
        """Test owner cannot leave bunch"""
        self.authenticate_user(self.user_token)
        bunch = Bunch.objects.create(
            name="Test Bunch",
            owner=self.user,
            is_private=True,
            invite_code="TEST123",
        )

        leave_url = f"/api/v1/bunch/{bunch.id}/leave/"
        response = self.client.post(leave_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Owner should not be able to leave",
        )
        self.assertTrue(
            Member.objects.filter(bunch=bunch, user=self.user).exists(),
            "Owner should still be a member",
        )

    def test_list_bunches_list_joined_ones(self):
        """Test listing bunches should list joined ones"""
        self.authenticate_user(self.user_token)
        bunch = Bunch.objects.create(
            name="Test Bunch",
            owner=self.user,
            is_private=True,
            invite_code="TEST123",
        )

        self.authenticate_user(self.other_token)  # Switch to other user
        join_url = f"/api/v1/bunch/{bunch.id}/join/"
        self.client.post(join_url, {"invite_code": "TEST123"})

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
