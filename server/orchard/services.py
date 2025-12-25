import logging

from django.conf import settings
from supabase import Client, create_client
from supabase_auth.types import (
    AdminUserAttributes,
    UserAttributes,
    UserResponse,
)

logger = logging.getLogger(__name__)


class SupabaseService:
    """
    Encapsulates Supabase service interactions. Only .get_user() is used for now.
    """

    def __init__(self, session=None):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_SECRET_KEY
        )
        if session:
            self.supabase.auth.set_session(
                session.get("access_token"), session.get("refresh_token")
            )
        self.service_client: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_SECRET_KEY
        )

    def sign_up(self, email: str, password: str):
        """Sign up a new user"""
        try:
            response = self.supabase.auth.sign_up(
                {"email": email, "password": password}
            )
            return response
        except Exception as e:
            logger.error(f"Error signing up: {str(e)}")
            return None

    def sign_in(self, email: str, password: str):
        """Sign in a user"""
        try:
            logger.debug(f"Attempting to sign in user: {email}")
            response = self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            if (
                response
                and hasattr(response, "user")
                and hasattr(response, "session")
                and response.user is not None
            ):
                logger.debug(f"Successfully signed in user: {response.user.id}")
                return {"user": response.user, "session": response.session}
            else:
                logger.error("Invalid response from Supabase auth")
                return None

        except Exception as e:
            logger.error(f"Error signing in: {str(e)}")
            return None

    def sign_out(self):
        """Sign out the current user."""
        self.supabase.auth.sign_out()

    def get_user(self, jwt: str | None = None) -> UserResponse | None:
        """Get the current user's data."""
        return self.supabase.auth.get_user(jwt)

    def update_user(self, data: UserAttributes):
        """Update a user's data."""
        try:
            response = self.supabase.auth.update_user(data)
            return response
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return None

    def update_user_admin(self, user_id: str, data: AdminUserAttributes):
        """Update a user's data via admin perms."""
        try:
            response = self.service_client.auth.admin.update_user_by_id(
                user_id, data
            )
            return response
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return None
