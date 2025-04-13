from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from bunch.models import Bunch, Channel, Member
from bunch.permissions import (
    AuthedHttpRequest,
    IsBunchAdmin,
    IsBunchMember,
    IsBunchOwner,
)
from bunch.serializers import (
    BunchSerializer,
    ChannelSerializer,
    MemberSerializer,
)
from users.models import User


class BunchViewSet(viewsets.ModelViewSet):
    serializer_class = BunchSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsBunchOwner,
    ]
    lookup_field = "id"

    def get_queryset(self):
        self.request: AuthedHttpRequest
        all_bunches = Bunch.objects.all()
        user_memberships = (
            self.request.user.bunch_memberships.all()
        )
        queryset = Bunch.objects.filter(
            members__user=self.request.user
        ).order_by("-created_at")

        if not queryset.exists() and all_bunches.exists():
            if not user_memberships.exists():
                # for testing -- return all bunches if the user not part of any
                return all_bunches.order_by("-created_at")

        return queryset

    def get_permissions(self):
        if self.action == "join":
            self.permission_classes = [
                permissions.IsAuthenticated
            ]
        elif self.action == "leave":
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
            ]
        else:
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchOwner,
            ]
        return super().get_permissions()

    def perform_create(self, serializer):
        bunch = serializer.save(owner=self.request.user)
        Member.objects.get_or_create(
            user=self.request.user,
            bunch=bunch,
            role="owner",
        )

    @action(detail=True, methods=["post"])
    def join(self, request, id=None):
        bunch = self.get_object()
        if (
            bunch.is_private
            and not bunch.invite_code
            == request.data.get("invite_code")
        ):
            return Response(
                {"error": "Invalid invite code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Member.objects.filter(
            bunch=bunch, user=request.user
        ).exists():
            return Response(
                {"error": "Already a member"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        member = Member.objects.create(
            user=request.user, bunch=bunch, role="member"
        )
        serializer = MemberSerializer(
            member, context={"request": request}
        )
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"])
    def leave(self, request, id=None):
        bunch = self.get_object()
        member = get_object_or_404(
            Member, user=request.user, bunch=bunch
        )
        # owner cannot leave their own bunch
        if member.role == "owner":
            return Response(
                {"error": "Owner cannot leave the bunch"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MemberViewSet(viewsets.ModelViewSet):
    serializer_class = MemberSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsBunchMember,
    ]
    lookup_field = "id"

    def get_queryset(self):
        bunch_id = self.kwargs.get("bunch_id")
        return Member.objects.filter(
            bunch_id=bunch_id
        ).order_by("-joined_at")

    def get_permissions(self):
        if self.action == "update_role":
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchAdmin,
            ]
        else:
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
            ]
        return super().get_permissions()

    def perform_create(self, serializer):
        bunch = get_object_or_404(
            Bunch, id=self.kwargs.get("bunch_id")
        )

        # from 'user' field or default to current user
        user_id = self.request.POST.get("user")
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise ValidationError("User not found.")
        else:
            user = self.request.user
        if Member.objects.filter(
            bunch=bunch, user=user
        ).exists():
            raise ValidationError(
                "User is already a member of this bunch."
            )

        nickname = self.request.POST.get("nickname")
        role = self.request.POST.get("role")

        serializer.save(
            bunch=bunch,
            user=user,
            nickname=nickname,
            role=role,
        )

    @action(detail=True, methods=["post"])
    def update_role(self, request, bunch_id=None, id=None):
        member = self.get_object()
        if not request.user.bunch_memberships.filter(
            bunch=member.bunch, role__in=["owner", "admin"]
        ).exists():
            return Response(
                {
                    "error": "You don't have permission to update roles"
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        new_role = request.data.get("role")
        if new_role not in dict(Member.ROLE_CHOICES):
            return Response(
                {"error": "Invalid role"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        member.role = new_role
        member.save()

        # Return serialized member with updated role
        serializer = MemberSerializer(
            member, context={"request": request}
        )
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )


class ChannelViewSet(viewsets.ModelViewSet):
    serializer_class = ChannelSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsBunchMember,
    ]
    lookup_field = "id"

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "DELETE"]:
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchAdmin,
            ]
        else:
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
            ]

        return super().get_permissions()

    def get_queryset(self):
        bunch_id = self.kwargs.get("bunch_id")
        return Channel.objects.filter(
            bunch_id=bunch_id
        ).order_by("created_at")

    def perform_create(self, serializer):
        bunch = get_object_or_404(
            Bunch, id=self.kwargs.get("bunch_id")
        )
        serializer.save(bunch=bunch)
