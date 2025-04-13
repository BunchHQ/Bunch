import uuid
from typing import TYPE_CHECKING

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

    def __str__(self):
        return self.name

    if TYPE_CHECKING:
        channels: models.QuerySet["Channel"]
        members: models.QuerySet["Member"]

    class Meta:
        verbose_name = "Bunch"
        verbose_name_plural = "Bunches"


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

    def __str__(self):
        return f"{self.name} in {self.bunch.name}"
