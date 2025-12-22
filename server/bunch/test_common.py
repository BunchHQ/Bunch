from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser

ROOT_TOKEN = "root_token"
USER_TOKEN = "user_token"
OTHER_TOKEN = "other_token"


def get_mocks(logger, cls):
    # Patch SupabaseJWTAuthentication.authenticate
    def mock_authenticate(self, request):
        token = (
            request.META.get("HTTP_AUTHORIZATION", "")
            .replace("Bearer ", "")
            .strip()
        )

        logger.debug(f"Mock JWT Auth token={token}")
        user_map = {
            cls.root_token: cls.root_user,
            cls.user_token: cls.user,
            cls.other_token: cls.other_user,
        }

        if token not in user_map:
            logger.warning(f"Mock JWT Auth token={token} not found")
            return (None, None)
        return (user_map[token], None)

    # patch SupabaseAuthMiddleware
    def mock_auth_middleware(self, request):
        if request.user.is_authenticated:
            return self.get_response(request)

        token = (
            request.META.get("HTTP_AUTHORIZATION", "")
            .replace("Bearer ", "")
            .strip()
        )

        logger.debug(f"Mock Auth Middleware token={token}")
        user_map = {
            cls.root_token: cls.root_user,
            cls.user_token: cls.user,
            cls.other_token: cls.other_user,
        }
        if token not in user_map:
            logger.warning(f"Mock Auth Middleware token={token} not found")
            request.user = AnonymousUser()
            return self.get_response(request)

        request.user = user_map[token]
        return self.get_response(request)

    def mock_session_middleware(self, request):
        if request.user.is_authenticated:
            request.supabase = None
        else:
            logger.warning(
                f"Mock Session Middleware user={request.user} not authenticated"
            )
            request.supabase = None

    auth_patch = patch(
        "orchard.authentication.SupabaseJWTAuthentication.authenticate",
        new=mock_authenticate,
    )
    auth_middleware_patch = patch(
        "orchard.middleware.SupabaseAuthMiddleware.__call__",
        new=mock_auth_middleware,
    )
    session_middleware_patch = patch(
        "orchard.middleware.SupabaseSessionMiddleware.process_request",
        new=mock_session_middleware,
    )

    return auth_patch, auth_middleware_patch, session_middleware_patch
