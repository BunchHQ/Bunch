from typing import override

from bunch.models import Bunch, Channel, Member, Message, Reaction, RoleChoices
from bunch.permissions import (AuthedHttpRequest, IsBunchAdmin, IsBunchMember,
                               IsBunchOwner, IsBunchPublic, IsMessageAuthor,
                               IsSelfMember)
from bunch.serializers import (BunchSerializer, ChannelSerializer,
                               MemberSerializer, MessageSerializer,
                               ReactionSerializer)
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
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
        # allow all access to superuser
        if (
            self.request.user
            and self.request.user.is_superuser
        ):
            return Bunch.objects.all()

        if self.action in ("list", "destroy"):
            # return all bunches the user is in
            queryset = Bunch.objects.filter(
                members__user=self.request.user
            )
        elif (
            self.action == "join" or self.action == "leave"
        ):
            # return all bunches
            queryset = Bunch.objects.all()
        else:
            # return all public bunches instead
            queryset = Bunch.objects.public()

        return queryset

    @override
    def get_permissions(self):
        if (
            self.request.user
            and self.request.user.is_superuser
        ):
            self.permission_classes = [
                permissions.IsAdminUser
            ]

            return super().get_permissions()

        if self.action == "list":
            # for listing joined bunches, auth is must and must be a member
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
            ]
        elif self.action == "retrieve":
            self.permission_classes = [
                permissions.IsAuthenticated,
                # allow retrieving any bunch by id if it's public or is a bunch member
                IsBunchPublic | IsBunchMember,
            ]
        elif self.action == "create":
            # creation allowed by all authenticated users
            self.permission_classes = [
                permissions.IsAuthenticated
            ]
        elif (
            self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchOwner | IsBunchAdmin,
            ]
        elif self.action == "public":
            self.permission_classes = [
                IsBunchPublic,
            ]
        elif self.action == "join":
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

    def perform_create(self, serializer: BunchSerializer):
        bunch: Bunch = serializer.save(
            owner=self.request.user
        )
        Member.objects.get_or_create(
            user=self.request.user,
            bunch=bunch,
            role="owner",
        )

    @action(
        detail=False,
        methods=["GET"],
        # allow no-auth access to /public
        authentication_classes=[],
    )
    def public(self, request, id=None):
        public_bunches = Bunch.objects.public()

        page = self.paginate_queryset(public_bunches)

        if page is not None:
            serializer = BunchSerializer(
                page,
                context={"request": request},
                many=True,
            )
            return self.get_paginated_response(
                serializer.data
            )

        serializer = BunchSerializer(
            public_bunches,
            context={"request": request},
            many=True,
        )
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
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
        return Response(
            {
                "status": "success",
                "message": "left bunch",
            },
            status=status.HTTP_200_OK,
        )


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
            bunch__id=bunch_id
        ).order_by("-joined_at")

    @override
    def get_permissions(self):
        # allow all to super user
        if (
            self.request.user
            and self.request.user.is_superuser
        ):
            self.permission_classes = [
                permissions.IsAdminUser
            ]
            return super().get_permissions()

        if self.action == "list":
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
            ]
        elif self.action == "create":
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchOwner,
            ]
        elif self.action == "retrieve":
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
            ]
        elif self.action in (
            "update",
            "partial_update",
            "delete",
        ):
            # TDOD: disallow role update via PUT or PATCH
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsSelfMember,
            ]
        elif self.action == "update_role":
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
        if new_role not in RoleChoices.values:
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

    def get_queryset(self):
        bunch_id = self.kwargs.get("bunch_id")
        return Channel.objects.filter(
            bunch_id=bunch_id
        ).order_by("created_at")

    def get_permissions(self):
        if (
            self.request.user
            and self.request.user.is_superuser
        ):
            self.permission_classes = [
                permissions.IsAdminUser
            ]
            return super().get_permissions()

        if self.action == "list":
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
            ]
        elif self.action == "create":
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchAdmin,
            ]
        elif self.action == "retrieve":
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
            ]
        elif self.action == "send_message":
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
            ]
        elif self.action in [
            "update",
            "partial_update",
            "destroy",
        ]:
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchAdmin,
            ]
        else:
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchAdmin,
            ]

        return super().get_permissions()

    def perform_create(self, serializer):
        bunch = get_object_or_404(
            Bunch, id=self.kwargs.get("bunch_id")
        )
        serializer.save(bunch=bunch)

    @action(detail=True, methods=["post"])
    def send_message(self, request, bunch_id=None, id=None):
        channel: Channel = self.get_object()
        member: Member = get_object_or_404(
            Member, user=request.user, bunch__id=bunch_id
        )

        message = Message.objects.create(
            channel=channel,
            author=member,
            content=request.data.get("content"),
        )

        serializer = MessageSerializer(
            message, context={"request": request}
        )
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )


class MessagePagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsBunchMember,
        # TODO: IsChannelMember once we have channel permissions
    ]
    lookup_field = "id"
    pagination_class = MessagePagination

    def get_queryset(self):
        bunch_id = self.kwargs.get("bunch_id")
        queryset = Message.objects.for_bunch(bunch_id)
        
        # Filter by channel if channel parameter is provided
        channel_id = self.request.query_params.get("channel")
        if channel_id:
            queryset = queryset.filter(channel_id=channel_id)
        
        return queryset.order_by("created_at")

    @override
    def get_permissions(self):
        if (
            self.request.user
            and self.request.user.is_superuser
        ):
            self.permission_classes = [
                permissions.IsAdminUser
            ]
            return super().get_permissions()

        if self.action == "list":
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
            ]
        elif self.action == "retrieve":
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
            ]
        elif self.action == "create":
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
            ]
        elif self.action in (
            "update",
            "partial_update",
            "destroy",
        ):
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
                IsMessageAuthor,
            ]
        else:
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
            ]

        return super().get_permissions()

    def perform_create(self, serializer: MessageSerializer):
        bunch = get_object_or_404(
            Bunch, id=self.kwargs.get("bunch_id")
        )
        channel_id = self.request.data.get("channel_id")
        channel = get_object_or_404(
            Channel, id=channel_id, bunch=bunch
        )
        member = get_object_or_404(
            Member, user=self.request.user, bunch=bunch
        )
        serializer.save(author=member, channel=channel)


class ReactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing message reactions.
    Supports CRUD operations for emoji reactions on messages.
    """
    serializer_class = ReactionSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsBunchMember,
    ]
    lookup_field = "id"

    def get_queryset(self):
        bunch_id = self.kwargs.get("bunch_id")
        message_id = self.request.query_params.get("message_id")
        
        if message_id:
            return Reaction.objects.filter(
                message_id=message_id,
                message__channel__bunch_id=bunch_id
            ).order_by("-created_at")
        
        return Reaction.objects.filter(
            message__channel__bunch_id=bunch_id
        ).order_by("-created_at")

    @override
    def get_permissions(self):
        if (
            self.request.user
            and self.request.user.is_superuser
        ):
            self.permission_classes = [
                permissions.IsAdminUser
            ]
            return super().get_permissions()

        if self.action in ["list", "retrieve"]:
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
            ]
        elif self.action == "create":
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
            ]
        elif self.action in ("update", "partial_update", "destroy"):
            # Only allow users to delete their own reactions
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
            ]
        else:
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsBunchMember,
            ]

        return super().get_permissions()

    def perform_create(self, serializer: ReactionSerializer):
        """Create a reaction for a message."""
        message_id = self.request.data.get("message_id")
        message = get_object_or_404(
            Message, 
            id=message_id,
            channel__bunch_id=self.kwargs.get("bunch_id")
        )
        
        # Check if user already reacted with this emoji
        emoji = serializer.validated_data.get("emoji")
        existing_reaction = Reaction.objects.filter(
            message=message,
            user=self.request.user,
            emoji=emoji
        ).first()
        
        if existing_reaction:
            raise ValidationError(
                "You have already reacted to this message with this emoji."
            )
        
        serializer.save(user=self.request.user, message=message)

    def perform_destroy(self, instance):
        """Only allow users to delete their own reactions."""
        if instance.user != self.request.user:
            raise ValidationError(
                "You can only delete your own reactions."
            )
        super().perform_destroy(instance)

    @action(detail=False, methods=["post"])
    def toggle(self, request, bunch_id=None):
        """
        Toggle a reaction (add if doesn't exist, remove if exists).
        This is a more convenient endpoint for frontend usage.
        """
        message_id = request.data.get("message_id")
        emoji = request.data.get("emoji")
        
        if not message_id or not emoji:
            return Response(
                {"error": "message_id and emoji are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        message = get_object_or_404(
            Message,
            id=message_id,
            channel__bunch_id=bunch_id
        )

        # Check if reaction already exists
        existing_reaction = Reaction.objects.filter(
            message=message,
            user=request.user,
            emoji=emoji
        ).first()

        if existing_reaction:
            # Remove reaction
            existing_reaction.delete()
            return Response(
                {"action": "removed", "emoji": emoji},
                status=status.HTTP_200_OK
            )
        else:
            # Add reaction
            reaction = Reaction.objects.create(
                message=message,
                user=request.user,
                emoji=emoji
            )
            serializer = ReactionSerializer(
                reaction, context={"request": request}
            )
            return Response(
                {
                    "action": "added",
                    "reaction": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
