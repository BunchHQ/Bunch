from typing import override

from django.urls import reverse
from rest_framework import serializers

from bunch.models import Bunch, Channel, Member, Message
from users.serializers import UserSerializer


class BunchSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    owner = UserSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Bunch
        fields = [
            "url",
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

    def get_url(self, obj):
        request = self.context.get("request")
        if request is None:
            return None
        return request.build_absolute_uri(
            reverse(
                "bunch:bunch-detail", kwargs={"id": obj.id}
            )
        )

    @override
    def create(self, validated_data):
        validated_data["owner"] = self.context[
            "request"
        ].user
        return super().create(validated_data)


class ChannelSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = [
            "url",
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

    def get_url(self, obj):
        request = self.context.get("request")
        if request is None:
            return None
        return request.build_absolute_uri(
            reverse(
                "bunch:bunch-channel-detail",
                kwargs={
                    "bunch_id": obj.bunch.id,
                    "id": obj.id,
                },
            )
        )


class MemberSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    username = serializers.CharField(
        source="user.username", read_only=True
    )

    class Meta:
        model = Member
        fields = [
            "url",
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

    def get_url(self, obj):
        request = self.context.get("request")
        if request is None:
            return None
        return request.build_absolute_uri(
            reverse(
                "bunch:bunch-member-detail",
                kwargs={
                    "bunch_id": obj.bunch.id,
                    "id": obj.id,
                },
            )
        )


class MessageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    channel = ChannelSerializer(read_only=True)
    channel_name = serializers.CharField(
        source="channel.name", read_only=True
    )
    author = MemberSerializer(read_only=True)
    author_username = serializers.CharField(
        source="author.user.username", read_only=True
    )

    class Meta:
        model = Message
        fields = [
            "url",
            "id",
            "content",
            "channel",
            "channel_name",
            "author",
            "author_username",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "channel",
            "author",
            "created_at",
        ]

    def get_url(self, obj):
        request = self.context.get("request")
        if request is None:
            return None
        return request.build_absolute_uri(
            reverse(
                "bunch:bunch-message-detail",
                kwargs={
                    "bunch_id": obj.channel.bunch.id,
                    "channel_id": obj.channel.id,
                    "id": obj.id,
                },
            )
        )
