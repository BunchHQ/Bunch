from django.http import HttpRequest
from rest_framework import permissions

from bunch.models import Message
from users.models import User


class AuthedHttpRequest(HttpRequest):
    user: User


class IsBunchOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a bunch to edit it.
    """

    def has_object_permission(
        self, request: AuthedHttpRequest, view, obj
    ):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.owner == request.user


class IsBunchMember(permissions.BasePermission):
    """
    Custom permission to only allow members of a bunch to access it.
    """

    def has_permission(
        self, request: AuthedHttpRequest, view
    ):
        if not request.user.is_authenticated:
            return False

        bunch_id = view.kwargs.get("bunch_id")
        if bunch_id:
            return request.user.bunch_memberships.filter(
                bunch_id=bunch_id
            ).exists()
        return True

    def has_object_permission(
        self, request: AuthedHttpRequest, view, obj
    ):
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

    def has_permission(
        self, request: AuthedHttpRequest, view
    ):
        if not request.user.is_authenticated:
            return False

        bunch_id = view.kwargs.get("bunch_id")
        if bunch_id:
            return request.user.bunch_memberships.filter(
                bunch_id=bunch_id,
                role__in=["owner", "admin"],
            ).exists()
        return True

    def has_object_permission(
        self, request: AuthedHttpRequest, view, obj
    ):
        return request.user.bunch_memberships.filter(
            bunch=obj.bunch, role__in=["owner", "admin"]
        ).exists()


class IsMessageAuthor(permissions.BasePermission):
    """
    Custom permission to only allow authors of a message to edit/delete it.
    """

    def has_object_permission(
        self, request: AuthedHttpRequest, view, obj: Message
    ):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user
