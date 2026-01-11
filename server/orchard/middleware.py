import logging
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from django.http.request import HttpRequest
from django.utils.deprecation import MiddlewareMixin
from supabase import AuthError

from orchard.services import SupabaseService
from users.models import User

logger = logging.getLogger(__name__)


class SupabaseAuthMiddleware:
    """
    Middleware to handle Supabase authentication.

    Tries to get the current user from Bearer JWT token, if valid, or creates a new shadow user.
    """

    def __init__(self, get_response):
        logger.debug("SupabaseAuthMiddleware")

        self.get_response = get_response
        self.supabase = SupabaseService()

    def __call__(self, request: HttpRequest):
        # Skip middleware if user is already authenticated
        if request.user.is_authenticated:
            logger.debug("user is authenticated")
            return self.get_response(request)

        auth_header = request.META.get("HTTP_AUTHORIZATION")

        if not auth_header or not auth_header.startswith("Bearer "):
            logger.debug("No valid JWT token provided")
            return self.get_response(request)

        token = auth_header.split(" ")[1]
        logger.debug(f"token is {token[:20]}...")

        if token:
            try:
                # Verify the token
                token_claims = self.supabase.get_claims(token)

                # Get or create the user
                if (
                    token_claims
                    and (user_id := token_claims.get("claims").get("sub"))
                    and (email := token_claims.get("claims").get("email"))
                ):
                    metadata = token_claims.get("claims").get(
                        "user_metadata", {}
                    )
                    try:
                        logger.debug(f"user_id is {user_id}")
                        user = User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        logger.debug("user does not exist, creating")
                        # Create a new user if they don't exist with fields we have already
                        user = User.objects.create(
                            id=user_id,
                            username=metadata.get("username"),
                            display_name=metadata.get("display_name"),
                            email=email,
                            password=make_password(None),
                        )
                        logger.debug(f"created user: {user}")

                    request.user = user
                    request.supabase_user_metadata = metadata
                    request.session["supabase_token"] = token

                    return self.get_response(request)
                else:
                    logger.debug("user with token not found or email not found")

            except AuthError as e:
                logger.debug(f"AuthError: {e.message}")

        logger.debug("user is anonymous")
        request.user = AnonymousUser()

        return self.get_response(request)


class SupabaseSessionMiddleware(MiddlewareMixin):
    """
    Middleware to handle Supabase session management.
    """

    def process_request(self, request: HttpRequest):
        if request.user.is_authenticated:
            # print(request.session.items())
            session = request.session.get("supabase_session")
            logger.debug(f"session={session}")
            if session:
                request.supabase = SupabaseService(session)
            else:
                request.supabase = SupabaseService()
        else:
            logger.debug(
                "SupabaseSessionMiddleware.process_request: user is not authenticated"
            )
            request.supabase = SupabaseService()


@database_sync_to_async
def get_supabase_user(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
        raise Exception("User not found. Please complete onboarding")

    return user


class SupabaseChannelsAuthMiddleware:
    """
    Middleware to handle Supabase authentication for channels.

    Tries to get the current user from Bearer JWT token, if valid.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Extract token from query string: ws://.../?token=XYZ
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        if token:
            try:
                # Verify the token
                token_claims = self.supabase.get_claims(token)

                # Get or create the user
                if token_claims and (
                    user_id := token_claims.get("claims").get("sub")
                ):
                    # Fetch/Create the Shadow User in the DB
                    scope["user"] = await get_supabase_user(user_id)
            except Exception:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)
