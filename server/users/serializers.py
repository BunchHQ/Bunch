from typing import override

from django.contrib.auth.models import Group
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "url",
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
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
            "groups",
        ]

    @override
    def create(self, validated_data: dict):
        groups_data = validated_data.pop("groups")
        user = User.objects.create_user(**validated_data)
        user.groups.set(groups_data)
        return user


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]
