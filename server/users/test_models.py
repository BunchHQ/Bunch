from typing import override

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from users.models import ColorChoices, ThemePreferenceChoices, User


class UserModelTest(TestCase):
    @override
    def setUp(self):
        User.objects.create_user(username="test", email="test@bunch.io", password="testpassword")
        User.objects.create_superuser(username="root", email="root@bunch.io", password="rootpassword")

    def test_creation(self):
        user = User.objects.get(email="test@bunch.io")
        self.assertEqual(user.username, "test", "Username is not correct")
        self.assertEqual(user.email, "test@bunch.io", "Email is not correct")
        self.assertTrue(user.check_password("testpassword"), "Password is not correct")
        self.assertEqual(str(user), user.username, "String representation of user is not username")

    def test_creation_with_invalid_username(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(username="", email="test@bunch.io", password="testpassword")

    def test_creation_with_invalid_email(self):
        with self.assertRaises(ValidationError, msg="Email is required."):
            User.objects.create_user(username="test2", email="", password="testpassword")

    def test_username_is_unique(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username="test", email="test2@bunch.io", password="testpassword")

    def test_email_is_unique(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username="test2", email="test@bunch.io", password="testpassword")

    def test_email_is_required(self):
        with self.assertRaises(ValidationError, msg="Email is required."):
            User.objects.create_user(username="test", password="testpassword")

    def test_default_theme_preference_is_system(self):
        user = User.objects.get(email="test@bunch.io")
        self.assertEqual(user.theme_preference, ThemePreferenceChoices.SYSTEM, "Default theme preference is not system")

    def test_default_color_is_set(self):
        user = User.objects.get(email="test@bunch.io")
        self.assertIn(user.color, ColorChoices.values)

    def test_default_color_for_superuser_is_silver(self):
        user = User.objects.get(email="root@bunch.io")
        self.assertEqual(user.color, ColorChoices.SILVER.value)

    def test_all_attributes(self):
        user = User.objects.get(email="test@bunch.io")
        self.assertTrue(user.is_active, "User is not active")
        self.assertFalse(user.is_staff, "User is staff")
        self.assertFalse(user.is_superuser, "User is superuser")

        root = User.objects.get(email="root@bunch.io")
        self.assertTrue(root.is_active, "Root user is not active")
        self.assertTrue(root.is_staff, "Root user is not staff")
        self.assertTrue(root.is_superuser, "Root user is not superuser")

        self.assertTrue(hasattr(user, "id"), "User does not have id attribute")
        self.assertTrue(hasattr(user, "email"), "User does not have email attribute")
        self.assertTrue(hasattr(user, "avatar"), "User does not have avatar attribute")
        self.assertTrue(hasattr(user, "status"), "User does not have status attribute")
        self.assertTrue(hasattr(user, "bio"), "User does not have bio attribute")
        self.assertTrue(hasattr(user, "theme_preference"), "User does not have theme_preference attribute")
        self.assertTrue(hasattr(user, "color"), "User does not have color attribute")
        self.assertTrue(hasattr(user, "pronoun"), "User does not have pronoun attribute")
