import random
import uuid
from typing import TYPE_CHECKING, override

from django.db import models

from users.models import User


class RoleChoices(models.TextChoices):
    OWNER = "owner", "Owner"
    ADMIN = "admin", "Admin"
    MEMBER = "member", "Member"


class ChannelTypes(models.TextChoices):
    TEXT = "text", "Text Channel"
    VOICE = "voice", "Voice Channel"
    ANNOUNCEMENT = "announcement", "Announcement Channel"


class ColorChoices(models.TextChoices):
    MIDNIGHT = "#2c3e50", "Midnight"
    SUNSET = "#f39c12", "Sunset"
    OCEAN = "#1a5276", "Ocean"
    FOREST = "#27ae60", "Forest"
    BURGUNDY = "#7b241c", "Burgundy"
    LILAC = "#af7ac5", "Lilac"
    TURQUOISE = "#48c9b0", "Turquoise"
    GRAPHITE = "#707b7c", "Graphite"
    PEACH = "#f5cba7", "Peach"
    NAVY = "#1f618d", "Navy"
    OLIVE = "#7d8c42", "Olive"
    MAROON = "#800000", "Maroon"
    AQUA = "#00ffff", "Aqua"
    ORCHID = "#da70d6", "Orchid"
    CHARCOAL = "#333333", "Charcoal"
    SALMON = "#fa8072", "Salmon"


def get_random_color_choice() -> str:
    """
    Returns a :class:`ColorChoices` for a bunch.

    Returns:
        A ColorChoice value
    """
    return random.choice(ColorChoices.values)


class BunchManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def public(self):
        """Get only public bunches."""
        return self.get_queryset().filter(is_private=False)


class Bunch(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_bunches",
    )
    icon = models.ImageField(
        upload_to="bunch_icons/", null=True, blank=True
    )
    is_private = models.BooleanField(default=False)
    invite_code = models.CharField(
        max_length=10, unique=True, null=True, blank=True
    )
    primary_color = models.CharField(
        max_length=7,
        help_text="Bunch's Primary color",
        choices=ColorChoices.choices,
        blank=True,
    )

    def __str__(self):
        return self.name

    if TYPE_CHECKING:
        channels: models.QuerySet["Channel"]
        members: models.QuerySet["Member"]

    @override
    def save(self, *args, **kwargs):
        self.clean()

        if not self.primary_color:
            self.primary_color = get_random_color_choice()

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Bunch"
        verbose_name_plural = "Bunches"
        ordering = ["-updated_at"]

    objects: "BunchManager" = BunchManager()


class Member(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    bunch = models.ForeignKey(
        Bunch,
        on_delete=models.CASCADE,
        related_name="members",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bunch_memberships",
    )
    role = models.CharField(
        max_length=10,
        help_text="Member's role in Bunch",
        choices=RoleChoices.choices,
        default=RoleChoices.MEMBER,
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    nickname = models.CharField(max_length=32, blank=True)

    class Meta:
        unique_together = (
            "bunch",
            "user",
        )  # user can be member of a bunch only once
        verbose_name = "Member"
        verbose_name_plural = "Members"
        ordering = ["-joined_at"]

    def __str__(self):
        return f"{self.user.username} in {self.bunch.name}"


class Channel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    bunch = models.ForeignKey(
        Bunch,
        on_delete=models.CASCADE,
        related_name="channels",
    )
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=20,
        choices=ChannelTypes.choices,
        default=ChannelTypes.TEXT,
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ["position"]
        verbose_name = "Channel"
        verbose_name_plural = "Channels"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.name} in {self.bunch.name}"

    if TYPE_CHECKING:
        messages: models.QuerySet["Message"]


class MessageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def active(self):
        """Returns only non-deleted messages."""
        return self.get_queryset().filter(deleted=False)

    def deleted(self):
        """Returns only deleted messages."""
        return self.get_queryset().filter(deleted=True)

    def for_channel(self, channel_id):
        """Returns messages for a specific channel."""
        return self.get_queryset().filter(
            channel_id=channel_id
        )

    def for_bunch(self, bunch_id):
        """Returns messages in a specific bunch."""
        return self.get_queryset().filter(
            channel__bunch_id=bunch_id
        )

    def by_author(self, author_id):
        """Returns messages by a specific author."""
        return self.get_queryset().filter(
            author_id=author_id
        )

    def recent(self, limit=100):
        """Returns most recent messages."""
        return self.get_queryset().order_by("-created_at")[
            :limit
        ]


class Message(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    author = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)
    edit_count = models.PositiveIntegerField(default=0)

    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects: "MessageManager" = MessageManager()

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ["created_at"]

    def __str__(self):
        return f"Message by {self.author.user.username} in {self.channel.name}"

    @override
    def save(self, *args, **kwargs):
        self.clean()

        if self.created_at is not None:
            self.edit_count += 1

        super().save(*args, **kwargs)
