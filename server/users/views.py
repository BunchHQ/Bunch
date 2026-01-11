import logging
from typing import override

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from supabase_auth.types import UserResponse

from orchard.services import SupabaseService
from users.models import ColorChoices, User
from users.serializers import (
    UserSerializer,
)

logger = logging.getLogger(__name__)


class AuthenticatedRequest(Request):
    user: User
    supabase: SupabaseService
    supabase_user: UserResponse


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @override
    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [permissions.IsAdminUser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]

        return super().get_permissions()

    @action(detail=False, methods=["GET"])
    def me(self, request: AuthenticatedRequest):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["POST"])
    def onboard(self, request: AuthenticatedRequest):
        logger.info("Onboarding user")
        logger.debug(f"User: {request.user.__dict__}")

        if request.user.onboarded:
            logger.info("Onboarding already completed")
            return Response(
                {
                    "message": "Onboarding already completed. Update profile data instead"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data
        logger.debug(f"Onboarding payload: {data}")

        metadata = request.supabase_user_metadata.copy()
        logger.debug(f"Current user metadata: {metadata}")
        metadata["onboarded"] = True

        usr_avatar = data.get("avatar", "")
        usr_status = data.get("status", request.user.status)
        usr_bio = data.get("bio", request.user.bio)
        usr_theme_preference = data.get(
            "theme_preference", request.user.theme_preference
        )
        usr_color = data.get("color", request.user.color)
        usr_pronoun = data.get("pronoun", request.user.pronoun)

        if usr_color not in ColorChoices.values:
            logger.error("Invalid color choice")
            return Response(
                {"message": "Invalid color choice"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            request.supabase.update_user_admin(
                str(request.user.id), {"user_metadata": metadata}
            )
            logger.debug(f"Updated user metadata: {metadata}")

            user = User.objects.get(id=request.user.id)
            user.avatar = usr_avatar
            user.status = usr_status
            user.bio = usr_bio
            user.theme_preference = usr_theme_preference
            user.color = usr_color
            user.pronoun = usr_pronoun
            user.onboarded = True
            user.save()
            logger.debug(f"Updated user: {user}")
        except User.DoesNotExist:
            logger.error("User does not exist during onboarding")
            return Response(
                {"message": "User does not exist. Please complete onboarding."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error onboarding user: {e}")
            return Response(
                {"message": "Error updating user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = UserSerializer(user, context={"request": request})
        logger.info(f"User {user.id} onboarding completed")
        logger.debug(f"{serializer.data}")
        return Response(
            {
                "message": "Onboarding Completed",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


# Not used
# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """

#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer
#     permission_classes = [permissions.IsAuthenticated]
