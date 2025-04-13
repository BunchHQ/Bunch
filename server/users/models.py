import random
import uuid
from typing import TYPE_CHECKING, override

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

if TYPE_CHECKING:
    from bunch.models import Bunch, Member


class ThemePreferenceChoices(models.TextChoices):
    LIGHT = "light", "Light"
    DARK = "dark", "Dark"
    SYSTEM = "system", "System"


class ColorChoices(models.TextChoices):
    RUBY = "#c02c38", "Ruby"
    EMERALD = "#2ecc71", "Emerald"
    SAPPHIRE = "#3498db", "Sapphire"
    AMBER = "#e6b32e", "Amber"
    VIOLET = "#9b59b6", "Violet"
    CORAL = "#e67e22", "Coral"
    ROSE = "#e84393", "Rose"
    SLATE = "#34495e", "Slate"
    IVORY = "#f5f5f0", "Ivory"
    SILVER = "#bdc3c7", "Silver"
    TEAL = "#16a085", "Teal"
    CRIMSON = "#e74c3c", "Crimson"
    LAVENDER = "#967bb6", "Lavender"
    MINT = "#00b894", "Mint"
    INDIGO = "#5352ed", "Indigo"
    HONEY = "#fbc531", "Honey"


def get_random_color_choice(user: "User") -> str:
    """
    Returns a :class:`ColorChoices` for a user.

    Superusers always get the ColorChoices.SILVER color, while other users
    get a randomly assigned color from the available choices.

    Args:
        user: The User instance for whom to get a color

    Returns:
        A ColorChoice value
    """
    if user.is_superuser:
        return ColorChoices.SILVER.value

    return random.choice(ColorChoices.values)


class User(AbstractUser):
    """
    Custom User Model for orchard.
    Adds additional properties like avatar, status, bio etc..
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    email = models.EmailField(unique=True)
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        help_text="User's profile picture",
    )
    status = models.CharField(
        blank=True,
        null=True,
        max_length=30,
        help_text="User's status",
    )
    bio = models.TextField(
        blank=True, null=True, help_text="User's bio"
    )

    theme_preference = models.CharField(
        max_length=6,
        help_text="User's theme preference",
        choices=ThemePreferenceChoices.choices,
        default=ThemePreferenceChoices.SYSTEM,
        blank=True,
    )
    color = models.CharField(
        max_length=7,
        help_text="User's color preference",
        choices=ColorChoices.choices,
        blank=True,
    )
    pronoun = models.CharField(
        blank=True,
        null=True,
        max_length=12,
        help_text="User's pronoun",
    )

    @override
    def __str__(self) -> str:
        """String representation of the user (username)."""
        return self.username

    @override
    def clean(self):
        if not self.email:
            raise ValidationError("Email is required.")

        super().clean()

    @override
    def save(self, *args, **kwargs):
        self.clean()

        if not self.color:
            self.color = get_random_color_choice(self)

        super().save(*args, **kwargs)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    if TYPE_CHECKING:
        owned_bunches: models.QuerySet["Bunch"]
        bunch_memberships: models.QuerySet["Member"]
