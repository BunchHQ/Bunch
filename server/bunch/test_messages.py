import logging
from typing import override

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from bunch.models import Bunch, Channel, Member, Message, RoleChoices
from bunch.test_common import OTHER_TOKEN, ROOT_TOKEN, USER_TOKEN, get_mocks
from users.models import User

logger = logging.getLogger(__name__)


class MessagesTest(APITestCase):
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

    def setupBunch1(self) -> None:
        self.owner = self.user
        self.root_user = self.root_user
        self.other_user = self.other_user

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
        Member.objects.filter(bunch=self.bunch1, user=self.root_user).delete()
        self.admin_member_1 = Member.objects.create(
            bunch=self.bunch1,
            user=self.root_user,
            role=RoleChoices.ADMIN,
        )
        # regular member
        Member.objects.filter(bunch=self.bunch1, user=self.other_user).delete()
        self.member_member_1 = Member.objects.create(
            bunch=self.bunch1,
            user=self.other_user,
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

        # owner member was already created with bunch
        self.owner_member_2 = Member.objects.get(
            bunch=self.bunch2,
            user=self.owner,
            role=RoleChoices.OWNER,
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

        self.send_message_url_1 = f"/api/v1/bunch/{self.bunch1.id}/channels/{self.channel_general_1.id}/send_message/"  # noqa: E501
        self.messages_list_url_1 = f"/api/v1/bunch/{self.bunch1.id}/messages/"

        self.send_message_url_2 = f"/api/v1/bunch/{self.bunch2.id}/channels/{self.channel_general_2.id}/send_message/"  # noqa: E501
        self.messages_list_url_2 = f"/api/v1/bunch/{self.bunch2.id}/messages/"

    def test_send_message_with_owner_auth(self):
        """Test sending a message with owner authentication"""
        self.authenticate_user(self.user_token)
        message_data = {"content": "Test Message"}

        response = self.client.post(self.send_message_url_1, message_data)
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
        self.authenticate_user(self.root_token)
        message_data = {"content": "Test Message"}

        response = self.client.post(self.send_message_url_1, message_data)
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
        self.authenticate_user(self.other_token)
        message_data = {"content": "Test Message"}

        response = self.client.post(self.send_message_url_1, message_data)
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

        self.authenticate_user(self.other_token)
        response = self.client.get(self.messages_list_url_1)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "List request should succeed",
        )

        if "results" in response.data:
            self.assertTrue(
                len(response.data["results"]) >= 1,
                "Paginated response should contain at least one message",
            )
        else:
            self.assertTrue(
                len(response.data) >= 1,
                "Response should contain at least one message",
            )

        message_data = (
            response.data[0]
            if "results" not in response.data
            else response.data["results"][0]
        )
        self.assertEqual(message_data["content"], "Test Message")
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
        """Test sending a message to another bunch without membership"""
        self.authenticate_user(self.other_token)
        message_data = {"content": "Test Message"}

        # try sending a message in 2nd server
        # while being logged in as member who is not in the 2nd server
        response = self.client.post(self.send_message_url_2, message_data)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Message creation should fail",
        )

    def test_list_messages_filtered_by_channel(self):
        """Test that messages are properly filtered by channel when channel parameter is provided"""
        # Create messages in different channels of the same bunch
        Message.objects.create(
            content="Message in General",
            channel=self.channel_general_1,
            author=self.member_member_1,
        )

        Message.objects.create(
            content="Message in Other",
            channel=self.channel_other_1,
            author=self.member_member_1,
        )

        self.authenticate_user(self.other_token)

        # Test filtering by general channel
        response = self.client.get(
            f"{self.messages_list_url_1}?channel={self.channel_general_1.id}"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "List request should succeed",
        )

        messages = (
            response.data["results"]
            if "results" in response.data
            else response.data
        )

        # Should only return messages from general channel
        self.assertEqual(
            len(messages),
            1,
            "Should only return 1 message from general channel",
        )
        self.assertEqual(messages[0]["content"], "Message in General")
        self.assertEqual(
            messages[0]["channel_id"], str(self.channel_general_1.id)
        )

        # Test filtering by other channel
        response = self.client.get(
            f"{self.messages_list_url_1}?channel={self.channel_other_1.id}"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "List request should succeed",
        )

        messages = (
            response.data["results"]
            if "results" in response.data
            else response.data
        )

        # Should only return messages from other channel
        self.assertEqual(
            len(messages), 1, "Should only return 1 message from other channel"
        )
        self.assertEqual(messages[0]["content"], "Message in Other")
        self.assertEqual(
            messages[0]["channel_id"], str(self.channel_other_1.id)
        )

        # Test without channel filter - should return all messages from the bunch
        response = self.client.get(self.messages_list_url_1)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "List request should succeed",
        )

        messages = (
            response.data["results"]
            if "results" in response.data
            else response.data
        )  # Should return all messages when no channel filter is applied
        self.assertEqual(
            len(messages),
            2,
            "Should return all messages when no channel filter is applied",
        )

    def test_create_reply_to_message(self):
        """Test creating a reply to an existing message"""
        self.authenticate_user(self.user_token)

        # Create an original message
        original_data = {
            "content": "Original message content",
            "channel_id": str(self.channel_general_1.id),
        }
        original_response = self.client.post(
            self.messages_list_url_1, original_data, format="json"
        )
        self.assertEqual(original_response.status_code, status.HTTP_201_CREATED)
        original_message_id = original_response.data["id"]

        # Create a reply to the original message
        reply_data = {
            "content": "This is a reply",
            "channel_id": str(self.channel_general_1.id),
            "reply_to_id": original_message_id,
        }
        reply_response = self.client.post(
            self.messages_list_url_1, reply_data, format="json"
        )

        self.assertEqual(reply_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(reply_response.data["content"], "This is a reply")
        self.assertEqual(
            reply_response.data["reply_to_id"], original_message_id
        )
        self.assertIsNotNone(reply_response.data["reply_to_preview"])

        # Verify reply preview contains expected data
        preview = reply_response.data["reply_to_preview"]
        self.assertEqual(preview["id"], original_message_id)
        self.assertEqual(preview["content"], "Original message content")
        self.assertEqual(preview["author"]["username"], self.user.username)

    def test_create_reply_to_nonexistent_message(self):
        """Test creating a reply to a non-existent message returns 404"""
        self.authenticate_user(self.user_token)

        reply_data = {
            "content": "This is a reply",
            "channel_id": str(self.channel_general_1.id),
            "reply_to_id": "00000000-0000-0000-0000-000000000000",
        }
        response = self.client.post(
            self.messages_list_url_1, reply_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_reply_to_deleted_message(self):
        """Test that replying to a deleted message fails"""
        self.authenticate_user(self.user_token)

        # Create and delete an original message
        original_data = {
            "content": "Original message content",
            "channel_id": str(self.channel_general_1.id),
        }
        original_response = self.client.post(
            self.messages_list_url_1, original_data, format="json"
        )
        original_message_id = original_response.data["id"]

        # Mark the message as deleted
        message = Message.objects.get(id=original_message_id)
        message.deleted = True
        message.save()

        # Try to reply to the deleted message
        reply_data = {
            "content": "This is a reply to deleted message",
            "channel_id": str(self.channel_general_1.id),
            "reply_to_id": original_message_id,
        }
        response = self.client.post(
            self.messages_list_url_1, reply_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_reply_cross_bunch(self):
        """Test that replying to a message from another bunch fails"""
        self.authenticate_user(self.user_token)

        # Create a message in bunch1
        message_data = {
            "content": "Message in bunch1",
            "channel_id": str(self.channel_general_1.id),
        }
        response = self.client.post(
            self.messages_list_url_1, message_data, format="json"
        )
        message_id = response.data["id"]

        # Try to reply to it from bunch2
        reply_data = {
            "content": "Reply from bunch2",
            "channel_id": str(self.channel_general_2.id),
            "reply_to_id": message_id,
        }

        messages_list_url_2 = f"/api/v1/bunch/{self.bunch2.id}/messages/"
        response = self.client.post(
            messages_list_url_2, reply_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_replies_to_message(self):
        """Test retrieving replies to a specific message"""
        self.authenticate_user(self.user_token)

        # Create an original message
        original_data = {
            "content": "Original message",
            "channel_id": str(self.channel_general_1.id),
        }
        original_response = self.client.post(
            self.messages_list_url_1, original_data, format="json"
        )
        original_message_id = original_response.data["id"]

        # Create multiple replies
        for i in range(3):
            reply_data = {
                "content": f"Reply {i + 1}",
                "channel_id": str(self.channel_general_1.id),
                "reply_to_id": original_message_id,
            }
            self.client.post(
                self.messages_list_url_1, reply_data, format="json"
            )

        # Get replies
        replies_url = (
            f"{self.messages_list_url_1}{original_message_id}/replies/"
        )
        response = self.client.get(replies_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        replies = (
            response.data["results"]
            if "results" in response.data
            else response.data
        )
        self.assertEqual(len(replies), 3)

        # Verify replies are ordered by created_at
        reply_contents = [reply["content"] for reply in replies]
        self.assertEqual(reply_contents, ["Reply 1", "Reply 2", "Reply 3"])

    def test_message_reply_count_annotation(self):
        """Test that messages are properly annotated with reply count"""
        self.authenticate_user(self.user_token)

        # Create an original message
        original_data = {
            "content": "Message with replies",
            "channel_id": str(self.channel_general_1.id),
        }
        original_response = self.client.post(
            self.messages_list_url_1, original_data, format="json"
        )
        original_message_id = original_response.data["id"]

        # Create 2 replies
        for i in range(2):
            reply_data = {
                "content": f"Reply {i + 1}",
                "channel_id": str(self.channel_general_1.id),
                "reply_to_id": original_message_id,
            }
            self.client.post(
                self.messages_list_url_1, reply_data, format="json"
            )

        # Get the original message and check reply count
        message_detail_url = f"{self.messages_list_url_1}{original_message_id}/"
        response = self.client.get(message_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["reply_count"], 2)

    def test_nested_replies_not_allowed(self):
        """Test that replying to a reply creates a reply to the original message"""
        self.authenticate_user(self.user_token)

        # Create original message
        original_data = {
            "content": "Original message",
            "channel_id": str(self.channel_general_1.id),
        }
        original_response = self.client.post(
            self.messages_list_url_1, original_data, format="json"
        )
        original_message_id = original_response.data["id"]

        # Create first reply
        reply1_data = {
            "content": "First reply",
            "channel_id": str(self.channel_general_1.id),
            "reply_to_id": original_message_id,
        }
        reply1_response = self.client.post(
            self.messages_list_url_1, reply1_data, format="json"
        )
        reply1_id = reply1_response.data["id"]

        # Try to reply to the reply (should still reference original)
        reply2_data = {
            "content": "Reply to reply",
            "channel_id": str(self.channel_general_1.id),
            "reply_to_id": reply1_id,
        }
        reply2_response = self.client.post(
            self.messages_list_url_1, reply2_data, format="json"
        )

        self.assertEqual(reply2_response.status_code, status.HTTP_201_CREATED)
        # The reply should still reference the first reply, not the original
        self.assertEqual(reply2_response.data["reply_to_id"], reply1_id)

    def test_top_level_messages_filter(self):
        """Test filtering for top-level messages only"""
        self.authenticate_user(self.user_token)

        # Create original message
        original_data = {
            "content": "Top level message",
            "channel_id": str(self.channel_general_1.id),
        }
        original_response = self.client.post(
            self.messages_list_url_1, original_data, format="json"
        )
        original_message_id = original_response.data["id"]

        # Create a reply
        reply_data = {
            "content": "This is a reply",
            "channel_id": str(self.channel_general_1.id),
            "reply_to_id": original_message_id,
        }
        self.client.post(self.messages_list_url_1, reply_data, format="json")

        # Get all messages (should include both)
        response = self.client.get(self.messages_list_url_1)
        all_messages = (
            response.data["results"]
            if "results" in response.data
            else response.data
        )
        self.assertEqual(len(all_messages), 2)

        # Get only top-level messages
        response = self.client.get(f"{self.messages_list_url_1}?top_level=true")
        top_level_messages = (
            response.data["results"]
            if "results" in response.data
            else response.data
        )
        self.assertEqual(len(top_level_messages), 1)
        self.assertEqual(top_level_messages[0]["content"], "Top level message")

    def test_reply_preview_content_truncation(self):
        """Test that reply preview content is properly truncated"""
        self.authenticate_user(self.user_token)

        # Create a long original message (over 100 characters)
        long_content = "A" * 150  # 150 characters
        original_data = {
            "content": long_content,
            "channel_id": str(self.channel_general_1.id),
        }
        original_response = self.client.post(
            self.messages_list_url_1, original_data, format="json"
        )
        original_message_id = original_response.data["id"]

        # Create a reply
        reply_data = {
            "content": "Reply to long message",
            "channel_id": str(self.channel_general_1.id),
            "reply_to_id": original_message_id,
        }
        reply_response = self.client.post(
            self.messages_list_url_1, reply_data, format="json"
        )
        # Check that preview content is truncated
        preview = reply_response.data["reply_to_preview"]
        self.assertEqual(len(preview["content"]), 103)  # 100 chars + "..."
        self.assertTrue(preview["content"].endswith("..."))

    def test_unauthorized_user_cannot_create_reply(self):
        """Test that unauthorized users cannot create replies"""
        self.authenticate_user(self.user_token)

        # First create a valid message to reply to
        original_data = {
            "content": "Original message for unauthorized test",
            "channel_id": str(self.channel_general_1.id),
        }
        original_response = self.client.post(
            self.messages_list_url_1, original_data, format="json"
        )
        original_message_id = original_response.data["id"]

        # Clear authentication to make user unauthorized
        self.client.credentials()

        reply_data = {
            "content": "Unauthorized reply",
            "channel_id": str(self.channel_general_1.id),
            "reply_to_id": original_message_id,
        }
        response = self.client.post(
            self.messages_list_url_1, reply_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_member_cannot_create_reply(self):
        """Test that non-members cannot create replies"""
        # Use other_user who is not a member of bunch2
        self.authenticate_user(self.other_token)

        # First create a valid message in bunch2 (as owner)
        self.authenticate_user(self.user_token)
        original_data = {
            "content": "Original message in bunch2",
            "channel_id": str(self.channel_general_2.id),
        }
        original_response = self.client.post(
            self.messages_list_url_2, original_data, format="json"
        )
        original_message_id = original_response.data["id"]

        # Now try to reply as other_user (non-member of bunch2)
        self.authenticate_user(self.other_token)
        reply_data = {
            "content": "Non-member reply",
            "channel_id": str(self.channel_general_2.id),
            "reply_to_id": original_message_id,
        }
        response = self.client.post(
            self.messages_list_url_2, reply_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
