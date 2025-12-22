import logging
from typing import override

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from users.models import User
from users.serializers import (
    UserSerializer,
)

logger = logging.getLogger(__name__)


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
    def me(self, request: Request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["POST"])
    def onboard(self, request: Request):
        logger.info("Onboarding user")
        logger.debug(f"User: {request.user.__dict__}")

        if request.user.username:
            logger.info("Onboarding already completed")
            return Response(
                {
                    "message": "Onboarding already completed. Update profile data instead"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data
        logger.debug(f"Onboarding payload: {data}")

        usr_username = data.get("username")
        usr_first_name = data.get("first_name")
        usr_last_name = data.get("last_name")
        usr_avatar = data.get("avatar", "")
        usr_status = data.get("status", request.user.status)
        usr_bio = data.get("bio", request.user.bio)
        usr_theme_preference = data.get(
            "theme_preference", request.user.theme_preference
        )
        usr_color = data.get("color", request.user.color)
        usr_pronoun = data.get("pronoun", request.user.pronoun)

        if not all(
            [
                usr_username,
                usr_first_name,
                usr_last_name,
            ]
        ):
            logger.error("Missing required fields")
            return Response(
                {
                    "message": "Missing required fields. username, first_name and last_name are required."  # noqa: E501
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=request.user.id)
            user.username = usr_username
            user.first_name = usr_first_name
            user.last_name = usr_last_name
            user.avatar = usr_avatar
            user.status = usr_status
            user.bio = usr_bio
            user.theme_preference = usr_theme_preference
            user.color = usr_color
            user.pronoun = usr_pronoun
            user.save()
        except User.DoesNotExist:
            logger.error("User does not exist during onboarding")
            return Response(
                {"message": "User does not exist"},
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
