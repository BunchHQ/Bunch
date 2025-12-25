from typing import override

from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "url",
            "id",
            "email",
            "username",
            "display_name",
            "password",
            "is_active",
            "is_staff",
            "is_superuser",
            "avatar",
            "status",
            "bio",
            "theme_preference",
            "color",
            "pronoun",
            "onboarded",
            "groups",
        ]

    def get_url(self, obj: User) -> str | None:
        request = self.context.get("request")
        if request is None:
            return None
        return request.build_absolute_uri(
            reverse("user:user-detail", kwargs={"pk": obj.id})
        )

    @override
    def create(self, validated_data: dict):
        groups_data = None
        if "groups" in validated_data:
            groups_data = validated_data.pop("groups")

        user = User.objects.create_user(**validated_data)

        if groups_data:
            user.groups.set(groups_data)

        return user


class GroupSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ["url", "name"]

    def get_url(self, obj) -> str | None:
        request = self.context.get("request")
        if request is None:
            return None
        return request.build_absolute_uri(
            reverse("user:group-detail", kwargs={"pk": obj.id})
        )
