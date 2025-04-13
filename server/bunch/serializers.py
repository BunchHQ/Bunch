from django.contrib.auth import get_user_model
from rest_framework import serializers

from bunch.models import Bunch, Channel, Member
from users.serializers import UserSerializer

User = get_user_model()


class BunchSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Bunch
        fields = [
            "id",
            "name",
            "description",
            "is_private",
            "invite_code",
            "owner",
            "members_count",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "invite_code",
            "created_at",
        ]

    def get_members_count(self, obj):
        return obj.members.count()

    def create(self, validated_data):
        validated_data["owner"] = self.context[
            "request"
        ].user
        return super().create(validated_data)


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = [
            "id",
            "name",
            "type",
            "description",
            "bunch",
            "is_private",
            "position",
            "created_at",
        ]
        read_only_fields = ["id", "bunch", "created_at"]


class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    username = serializers.CharField(
        source="user.username", read_only=True
    )

    class Meta:
        model = Member
        fields = [
            "id",
            "user",
            "username",
            "bunch",
            "role",
            "nickname",
            "joined_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "bunch",
            "joined_at",
        ]
