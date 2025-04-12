import uuid

from django.db import models
from users.models import User


class Bunch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_bunches"
    )
    icon = models.ImageField(upload_to="bunch_icons/", null=True, blank=True)
    is_private = models.BooleanField(default=False)
    invite_code = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Member(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("member", "Member"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bunch = models.ForeignKey(Bunch, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bunch_memberships"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="member")
    joined_at = models.DateTimeField(auto_now_add=True)
    nickname = models.CharField(max_length=32, blank=True)

    class Meta:
        unique_together = ("bunch", "user")  # user can be member of a bunch only once

    def __str__(self):
        return f"{self.user.username} in {self.bunch.name}"


class Channel(models.Model):
    CHANNEL_TYPES = [
        ("text", "Text Channel"),
        ("voice", "Voice Channel"),
        ("announcement", "Announcement Channel"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bunch = models.ForeignKey(Bunch, on_delete=models.CASCADE, related_name="channels")
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=CHANNEL_TYPES, default="text")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.name} in {self.bunch.name}"
