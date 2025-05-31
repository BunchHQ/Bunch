import random
import uuid
from typing import TYPE_CHECKING, override

from django.core.validators import RegexValidator
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


# Common emoji choices for reactions
class EmojiChoices(models.TextChoices):
    THUMBS_UP = "👍", "Thumbs Up"
    THUMBS_DOWN = "👎", "Thumbs Down"
    HEART = "❤️", "Heart"
    LAUGHING = "😂", "Laughing"
    SURPRISED = "😮", "Surprised"
    ANGRY = "😠", "Angry"
    SAD = "😢", "Sad"
    PARTY = "🎉", "Party"
    FIRE = "🔥", "Fire"
    CLAP = "👏", "Clapping"
    EYES = "👀", "Eyes"
    THINKING = "🤔", "Thinking"


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
        default=get_random_color_choice,
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

    def with_replies(self):
        """Returns messages with their reply count."""
        return self.get_queryset().annotate(
            reply_count=models.Count("replies")
        )

    def top_level(self):
        """Returns only top-level messages (not replies)."""
        return self.get_queryset().filter(reply_to__isnull=True)

    def replies_to(self, message_id):
        """Returns replies to a specific message."""
        return self.get_queryset().filter(reply_to_id=message_id)


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
    
    # Reply functionality
    reply_to = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        help_text="Message this is a reply to",
    )

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

    if TYPE_CHECKING:
        reactions: models.QuerySet["Reaction"]


class ReactionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def for_message(self, message_id):
        """Returns reactions for a specific message."""
        return self.get_queryset().filter(message_id=message_id)

    def by_user(self, user_id):
        """Returns reactions by a specific user."""
        return self.get_queryset().filter(user_id=user_id)

    def by_emoji(self, emoji):
        """Returns reactions by a specific emoji."""
        return self.get_queryset().filter(emoji=emoji)

    def for_message_by_emoji(self, message_id, emoji):
        """Returns reactions for a specific message and emoji."""
        return self.get_queryset().filter(
            message_id=message_id, emoji=emoji
        )


class Reaction(models.Model):
    """
    Model representing emoji reactions to messages.
    Each user can only react once per message per emoji.
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="reactions",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="message_reactions",
    )
    emoji = models.CharField(
        max_length=10,
        help_text="Emoji character used for reaction",
        # Allow any Unicode emoji, not just predefined choices
        validators=[
            RegexValidator(
                regex=r'^[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u26FF\u2700-\u27BF]+$',
                message='Must be a valid emoji character',
                flags=0
            )
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects: "ReactionManager" = ReactionManager()

    class Meta:
        unique_together = ('message', 'user', 'emoji')  # One reaction per user per emoji per message
        verbose_name = "Reaction"
        verbose_name_plural = "Reactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['message', 'emoji']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.username} reacted {self.emoji} to message {self.message.id}"

    def clean(self):
        """Validate that the user has access to the message's channel/bunch."""
        super().clean()
        from django.core.exceptions import ValidationError

        # Check if user is a member of the bunch where the message was posted
        try:
            self.message.channel.bunch.members.get(user=self.user)
        except Member.DoesNotExist:
            raise ValidationError(
                "User must be a member of the bunch to react to messages."
            )
