from bunch.models import Bunch, Channel, Member, Message, Reaction, RoleChoices
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class ReactionsTestCase(APITestCase):
    def setUp(self):
        """Set up test data."""
        # Create users
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="testpass123"
        )
        self.member = User.objects.create_user(
            username="member", 
            email="member@example.com",
            password="testpass123"
        )
        
        # Create bunch
        self.bunch = Bunch.objects.create(
            name="Test Bunch",
            owner=self.owner
        )
        
        # Create channel
        self.channel = Channel.objects.create(
            bunch=self.bunch,
            name="general",
            type="text"
        )
        
        # Create members
        self.owner_member = Member.objects.get(
            bunch=self.bunch,
            user=self.owner,
            role=RoleChoices.OWNER
        )
        
        self.member_member = Member.objects.create(
            bunch=self.bunch,
            user=self.member,
            role=RoleChoices.MEMBER
        )
        
        # Create message
        self.message = Message.objects.create(
            content="Test message",
            author=self.owner_member,
            channel=self.channel
        )

    def test_create_reaction(self):
        """Test creating a new reaction."""
        self.client.force_authenticate(user=self.member)
        
        data = {
            "message_id": str(self.message.id),
            "emoji": "👍"
        }
        
        response = self.client.post(
            f"/api/v1/bunch/{self.bunch.id}/reactions/",
            data,
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["emoji"], "👍")
        self.assertEqual(response.data["user"]["id"], str(self.member.id))
        
        # Verify reaction was created in database
        reaction = Reaction.objects.get(id=response.data["id"])
        self.assertEqual(reaction.emoji, "👍")
        self.assertEqual(reaction.user, self.member)
        self.assertEqual(reaction.message, self.message)    
    
    def test_toggle_reaction_add(self):
        """Test adding a reaction via toggle endpoint."""
        self.client.force_authenticate(user=self.member)
        
        data = {
            "message_id": str(self.message.id),
            "emoji": "❤️"
        }
        
        response = self.client.post(
            f"/api/v1/bunch/{self.bunch.id}/reactions/toggle/",
            data,
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["action"], "added")
        self.assertEqual(response.data["reaction"]["emoji"], "❤️")
        
        # Verify reaction exists
        self.assertTrue(
            Reaction.objects.filter(
                message=self.message,
                user=self.member,
                emoji="❤️"
            ).exists()
        )

    def test_toggle_reaction_remove(self):
        """Test removing a reaction via toggle endpoint."""
        # First create a reaction
        reaction = Reaction.objects.create(
            message=self.message,
            user=self.member,
            emoji="😂"
        )
        
        self.client.force_authenticate(user=self.member)
        
        data = {
            "message_id": str(self.message.id),
            "emoji": "😂"
        }
        
        response = self.client.post(
            f"/api/v1/bunch/{self.bunch.id}/reactions/toggle/",
            data,
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], "removed")
        
        # Verify reaction was deleted
        self.assertFalse(
            Reaction.objects.filter(id=reaction.id).exists()
        )

    def test_duplicate_reaction_prevented(self):
        """Test that duplicate reactions are prevented."""
        # Create initial reaction
        Reaction.objects.create(
            message=self.message,
            user=self.member,
            emoji="🔥"
        )
        
        self.client.force_authenticate(user=self.member)
        
        data = {
            "message_id": str(self.message.id),
            "emoji": "🔥"
        }
        
        response = self.client.post(
            f"/api/v1/bunch/{self.bunch.id}/reactions/",
            data,
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reaction_counts_in_message_serializer(self):
        """Test that message serializer includes reaction counts."""
        # Create some reactions
        Reaction.objects.create(
            message=self.message,
            user=self.member,
            emoji="👍"
        )
        Reaction.objects.create(
            message=self.message,
            user=self.owner,
            emoji="👍"
        )
        Reaction.objects.create(
            message=self.message,
            user=self.member,
            emoji="❤️"
        )
        
        self.client.force_authenticate(user=self.member)
        
        response = self.client.get(
            f"/api/v1/bunch/{self.bunch.id}/messages/?channel={self.channel.id}"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find our message in the response
        message_data = None
        for msg in response.data["results"]:
            if msg["id"] == str(self.message.id):
                message_data = msg
                break
        
        self.assertIsNotNone(message_data)
        self.assertIn("reaction_counts", message_data)
        self.assertEqual(message_data["reaction_counts"]["👍"], 2)
        self.assertEqual(message_data["reaction_counts"]["❤️"], 1)

    def test_non_member_cannot_react(self):
        """Test that non-members cannot add reactions."""
        non_member = User.objects.create_user(
            username="nonmember",
            email="nonmember@example.com",
            password="testpass123"
        )
        
        self.client.force_authenticate(user=non_member)
        
        data = {
            "message_id": str(self.message.id),
            "emoji": "👍"
        }
        
        response = self.client.post(
            f"/api/v1/bunch/{self.bunch.id}/reactions/",
            data,
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_emoji_rejected(self):
        """Test that invalid emojis are rejected."""
        self.client.force_authenticate(user=self.member)
        
        data = {
            "message_id": str(self.message.id),
            "emoji": "not_an_emoji"
        }
        
        response = self.client.post(
            f"/api/v1/bunch/{self.bunch.id}/reactions/",
            data,
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
