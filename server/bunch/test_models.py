import uuid
from typing import override

from django.db.utils import IntegrityError
from django.test import TestCase

from bunch.models import (
    Bunch,
    Channel,
    ChannelTypes,
    Member,
    RoleChoices,
)
from users.models import User


class BunchModelTest(TestCase):
    @override
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.bunch = Bunch.objects.create(
            name="Test Bunch",
            description="Test Description",
            owner=self.user,
            is_private=False,
            invite_code="TEST123",
        )

    def test_bunch_creation(self):
        """Test bunch creation and string representation"""
        self.assertEqual(
            str(self.bunch),
            "Test Bunch",
            "Bunch string representation is not correct",
        )
        self.assertEqual(
            self.bunch.owner,
            self.user,
            "Bunch owner is not correct",
        )
        self.assertFalse(
            self.bunch.is_private,
            "Bunch is private when it should be public",
        )
        self.assertEqual(
            self.bunch.invite_code,
            "TEST123",
            "Bunch invite code is not correct",
        )
        self.assertIsNotNone(
            self.bunch.created_at,
            "Bunch created_at is not set",
        )
        self.assertIsNotNone(
            self.bunch.updated_at,
            "Bunch updated_at is not set",
        )

    def test_bunch_fields(self):
        """Test all bunch model fields"""
        self.assertIsInstance(
            self.bunch.id,
            uuid.UUID,
            "Bunch ID should be a UUID",
        )
        self.assertEqual(
            self.bunch.name,
            "Test Bunch",
            "Bunch name is not correct",
        )
        self.assertEqual(
            self.bunch.description,
            "Test Description",
            "Bunch description is not correct",
        )
        self.assertEqual(
            self.bunch.icon,
            None,
            "Bunch icon should be None by default",
        )

    def test_bunch_member_creation(self):
        """Test bunch member creation and unique constraint"""
        member = Member.objects.create(
            bunch=self.bunch,
            user=self.user,
            role=RoleChoices.MEMBER,
            nickname="TestNick",
        )
        self.assertEqual(
            str(member),
            f"{self.user.username} in {self.bunch.name}",
            "Member string representation is not correct",
        )
        self.assertEqual(
            member.nickname,
            "TestNick",
            "Member nickname is not correct",
        )

        with self.assertRaises(
            Exception,
            msg="Member creation should fail for duplicate user in same bunch",
        ):
            Member.objects.create(
                bunch=self.bunch,
                user=self.user,
                role=RoleChoices.MEMBER,
            )

    def test_bunch_channel_creation(self):
        """Test bunch channel creation and ordering"""
        channel1 = Channel.objects.create(
            bunch=self.bunch,
            name="Channel 1",
            type=ChannelTypes.TEXT,
            description="Test Description",
            position=1,
            is_private=False,
        )
        channel2 = Channel.objects.create(
            bunch=self.bunch,
            name="Channel 2",
            type=ChannelTypes.VOICE,
            description="Voice Channel",
            position=2,
            is_private=True,
        )

        self.assertEqual(
            str(channel1),
            f"Channel 1 in {self.bunch.name}",
            "Channel string representation is not correct",
        )
        self.assertEqual(
            channel1.type,
            ChannelTypes.TEXT,
            "Channel type is not correct",
        )
        self.assertEqual(
            channel2.type,
            ChannelTypes.VOICE,
            "Channel type is not correct",
        )
        self.assertEqual(
            list(Channel.objects.all()),
            [channel1, channel2],
            "Channel ordering is not correct",
        )


class MemberModelTest(TestCase):
    @override
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="test1@example.com",
            password="testpass123",
            first_name="Test1",
            last_name="User1",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
            first_name="Test2",
            last_name="User2",
        )

        self.bunch = Bunch.objects.create(
            name="Test Bunch",
            description="Test Description",
            owner=self.user1,
        )

        self.member1 = Member.objects.create(
            bunch=self.bunch,
            user=self.user1,
            role=RoleChoices.OWNER,
            nickname="Owner",
        )

    def test_member_creation(self):
        """Test member creation and string representation"""
        self.assertEqual(
            str(self.member1),
            f"{self.user1.username} in {self.bunch.name}",
            "Member string representation is not correct",
        )
        self.assertEqual(
            self.member1.role,
            RoleChoices.OWNER,
            "Member role is not correct",
        )
        self.assertEqual(
            self.member1.nickname,
            "Owner",
            "Member nickname is not correct",
        )
        self.assertIsNotNone(
            self.member1.joined_at,
            "Member joined_at is not set",
        )
        self.assertIsInstance(
            self.member1.id,
            uuid.UUID,
            "Member ID should be a UUID",
        )

    def test_member_unique_constraint(self):
        """Test unique constraint between bunch and user"""
        # self.user1 is already a member in self.bunch
        with self.assertRaises(
            IntegrityError,
            msg="Member creation should fail for duplicate user in same bunch",
        ):
            Member.objects.create(
                bunch=self.bunch,
                user=self.user1,
                role=RoleChoices.MEMBER,
            )

    def test_multiple_members_per_bunch(self):
        """Test multiple members can belong to the same bunch"""
        Member.objects.create(
            bunch=self.bunch,
            user=self.user2,
            role=RoleChoices.MEMBER,
            nickname="Member",
        )

        self.assertEqual(
            Member.objects.filter(bunch=self.bunch).count(),
            2,  # (the owner, new member)
            "Bunch should have two members",
        )

    def test_member_roles(self):
        """Test member roles are enforced correctly"""
        # create member with admin role
        member2 = Member.objects.create(
            bunch=self.bunch,
            user=self.user2,
            role=RoleChoices.ADMIN,
            nickname="Admin",
        )

        self.assertEqual(
            member2.role,
            RoleChoices.ADMIN,
            "Member role should be 'admin'",
        )

        # update to member role
        member2.role = RoleChoices.MEMBER
        member2.save()
        member2.refresh_from_db()

        self.assertEqual(
            member2.role,
            RoleChoices.MEMBER,
            "Member role should be updated to 'member'",
        )


class ChannelModelTest(TestCase):
    @override
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.bunch = Bunch.objects.create(
            name="Test Bunch",
            description="Test Description",
            owner=self.user,
        )

    def test_channel_creation(self):
        """Test channel creation and string representation"""
        channel = Channel.objects.create(
            bunch=self.bunch,
            name="Test Channel",
            type="text",
            description="Test Description",
        )

        self.assertEqual(
            str(channel),
            f"Test Channel in {self.bunch.name}",
            "Channel string representation is not correct",
        )
        self.assertEqual(
            channel.type,
            "text",
            "Channel type is not correct",
        )
        self.assertEqual(
            channel.description,
            "Test Description",
            "Channel description is not correct",
        )
        self.assertFalse(
            channel.is_private,
            "Channel should be public by default",
        )
        self.assertEqual(
            channel.position,
            0,
            "Channel position should be 0 by default",
        )
        self.assertIsNotNone(
            channel.created_at,
            "Channel created_at is not set",
        )
        self.assertIsInstance(
            channel.id,
            uuid.UUID,
            "Channel ID should be a UUID",
        )

    def test_channel_types(self):
        """Test different channel types"""
        text_channel = Channel.objects.create(
            bunch=self.bunch,
            name="Text Channel",
            type=ChannelTypes.TEXT,
        )

        voice_channel = Channel.objects.create(
            bunch=self.bunch,
            name="Voice Channel",
            type=ChannelTypes.VOICE,
        )

        announcement_channel = Channel.objects.create(
            bunch=self.bunch,
            name="Announcement Channel",
            type=ChannelTypes.ANNOUNCEMENT,
        )

        self.assertEqual(
            text_channel.type,
            ChannelTypes.TEXT,
            "Channel type should be 'text'",
        )
        self.assertEqual(
            voice_channel.type,
            ChannelTypes.VOICE,
            "Channel type should be 'voice'",
        )
        self.assertEqual(
            announcement_channel.type,
            ChannelTypes.ANNOUNCEMENT,
            "Channel type should be 'announcement'",
        )

    def test_channel_ordering(self):
        """Test channel ordering by position"""
        channel3 = Channel.objects.create(
            bunch=self.bunch, name="Channel 3", position=3
        )

        channel1 = Channel.objects.create(
            bunch=self.bunch, name="Channel 1", position=1
        )

        channel2 = Channel.objects.create(
            bunch=self.bunch, name="Channel 2", position=2
        )

        channels = Channel.objects.filter(
            bunch=self.bunch
        ).order_by("position")
        self.assertEqual(
            channels[0],
            channel1,
            "First channel should be Channel 1",
        )
        self.assertEqual(
            channels[1],
            channel2,
            "Second channel should be Channel 2",
        )
        self.assertEqual(
            channels[2],
            channel3,
            "Third channel should be Channel 3",
        )

    def test_bunch_channel_relationship(self):
        """Test relationship between bunch and channels"""
        for i in range(3):
            Channel.objects.create(
                bunch=self.bunch,
                name=f"Channel {i}",
                position=i,
            )

        self.assertEqual(
            self.bunch.channels.count(),
            3,
            "Bunch should have 3 channels",
        )

        bunch_id = self.bunch.id
        self.bunch.delete()
        self.assertEqual(
            Channel.objects.filter(
                bunch_id=bunch_id
            ).count(),
            0,
            "Channels should be deleted when bunch is deleted",
        )
