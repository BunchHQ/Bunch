import logging
from typing import override

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AbstractBaseUser
from django.http import HttpRequest
from rest_framework import authentication, exceptions
from supabase import AuthError

from orchard.services import SupabaseService
from users.models import User

logger = logging.getLogger(__name__)


# probably unused for now, since we aren't using django's auth, so ignore implementation
class SupabaseAuth(BaseBackend):
    @override
    def authenticate(
        self,
        request: HttpRequest,
        username,
        password,
    ) -> AbstractBaseUser | None:
        logger.debug(f"Authenticating user: {username}")

        try:
            supabase = SupabaseService()
            result = supabase.sign_in(username, password) or {}
            logger.debug(f"Supabase sign-in result: {result}")

            user_data = result["user"]
            logger.debug(f"User data: {user_data}")

            session = result["session"]
            self.supabase_session = session

            # We find a 'shadow' user in Django's DB
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed(
                    "User not found. Please complete onboarding"
                )

            logger.debug(f"User found: {user}")

            return user
        except Exception:
            logger.error(
                f"Failed to authenticate user {username}", exc_info=True
            )

            return None

    @override
    def get_user(self, user_id) -> AbstractBaseUser | None:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExists:
            return None


class SupabaseJWTAuthentication(authentication.BaseAuthentication):
    """
    Verifies user JWT authentication using supabase for rest API and channels consumers
    """

    @override
    def authenticate(self, request):
        logger.debug("Authenticating user via JWT")

        auth_header = request.META.get("HTTP_AUTHORIZATION")

        if not auth_header or not auth_header.startswith("Bearer "):
            logger.debug("No valid JWT token provided")
            return None

        token = auth_header.split(" ")[1]
        logger.debug(f"JWT token received: {token[:20]}...")

        supabase = SupabaseService()
        try:
            token_user = supabase.get_user(token)
        except AuthError as e:
            logger.debug(f"Token error: {e}")
            raise exceptions.AuthenticationFailed("Token error")

        if not token_user:
            raise exceptions.AuthenticationFailed("Token user not found")

        user_id = token_user.user.id
        email = token_user.user.email

        logger.debug(f"User ID: {user_id}")
        logger.debug(f"Email: {email}")

        if not email:
            raise exceptions.AuthenticationFailed("Email not found in token")

        # We find a 'shadow' user in Django's DB
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                "User not found. Please complete onboarding"
            )

        return (user, None)
