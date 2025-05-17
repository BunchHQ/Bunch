from typing import override

from django.http import HttpRequest
from rest_framework import permissions

from bunch.models import Bunch, Member, Message, RoleChoices
from users.models import User


class AuthedHttpRequest(HttpRequest):
    user: User


class IsBunchPublic(permissions.BasePermission):
    """
    Custom permission to check if a bunch is public
    """

    @override
    def has_object_permission(
        self,
        request: AuthedHttpRequest,
        view,
        obj: Bunch,
    ) -> bool:
        return not obj.is_private


class IsBunchOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a bunch to edit it.
    """

    @override
    def has_permission(
        self, request: AuthedHttpRequest, view
    ) -> bool:
        if not request.user.is_authenticated:
            return False

        bunch_id = view.kwargs.get("bunch_id")
        if bunch_id:
            return request.user.owned_bunches.filter(
                id=bunch_id
            ).exists()
        return False

    @override
    def has_object_permission(
        self, request: AuthedHttpRequest, view, obj: Bunch
    ) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.owner == request.user


class IsBunchMember(permissions.BasePermission):
    """
    Custom permission to only allow members of a bunch to access it.
    """

    @override
    def has_object_permission(
        self, request: AuthedHttpRequest, view, obj
    ):
        if hasattr(obj, "author"):
            # for Message
            return request.user.bunch_memberships.filter(
                id=obj.author.id
            ).exists()
        if hasattr(obj, "bunch"):
            # for Member and Channel
            return request.user.bunch_memberships.filter(
                bunch=obj.bunch
            ).exists()
        elif type(obj).__name__ == "Bunch":
            # for Bunch
            return request.user.bunch_memberships.filter(
                bunch=obj
            ).exists()

        return False


class IsBunchAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admins of a bunch to perform certain actions.
    """

    @override
    def has_permission(
        self, request: AuthedHttpRequest, view
    ):
        if not request.user.is_authenticated:
            return False

        bunch_id = view.kwargs.get("bunch_id")
        if bunch_id:
            return request.user.bunch_memberships.filter(
                bunch_id=bunch_id,
                role__in=[
                    RoleChoices.OWNER,
                    RoleChoices.ADMIN,
                ],
            ).exists()
        return False

    @override
    def has_object_permission(
        self, request: AuthedHttpRequest, view, obj
    ):
        return request.user.bunch_memberships.filter(
            bunch=obj.bunch, role__in=["owner", "admin"]
        ).exists()


class IsSelfMember(permissions.BasePermission):
    """
    Custom permission to only allow users to uper their own memberships
    """

    @override
    def has_object_permission(
        self, request: AuthedHttpRequest, view, obj: Member
    ) -> bool:
        return obj.user == request.user


class IsMessageAuthor(permissions.BasePermission):
    """
    Custom permission to only allow authors of a message to edit/delete it.
    """

    @override
    def has_object_permission(
        self, request: AuthedHttpRequest, view, obj: Message
    ):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user
