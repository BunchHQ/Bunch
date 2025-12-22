from typing import override

from django.urls import reverse
from rest_framework import serializers

from bunch.models import Bunch, Channel, Member, Message, Reaction
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
            "primary_color",
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

    def get_members_count(self, obj: Bunch) -> int:
        return obj.members.count()

    def get_url(self, obj: Bunch) -> str | None:
        request = self.context.get("request")
        if request is None:
            return None
        return request.build_absolute_uri(
            reverse("bunch:bunch-detail", kwargs={"id": obj.id})
        )

    @override
    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
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

    def get_url(self, obj: Channel) -> str | None:
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
    username = serializers.CharField(source="user.username", read_only=True)

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

    def get_url(self, obj: Channel) -> str | None:
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


class ReactionSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    message_id = serializers.UUIDField(source="message.id", read_only=True)

    class Meta:
        model = Reaction
        fields = [
            "url",
            "id",
            "message_id",
            "user",
            "emoji",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "message_id",
            "user",
            "created_at",
        ]

    def get_url(self, obj: Reaction) -> str | None:
        request = self.context.get("request")
        if request is None:
            return None
        return request.build_absolute_uri(
            reverse(
                "bunch:bunch-reaction-detail",
                kwargs={
                    "bunch_id": obj.message.channel.bunch.id,
                    "id": obj.id,
                },
            )
        )

    def validate_emoji(self, value):
        """Validate that the emoji is a valid Unicode emoji."""
        import re

        emoji_pattern = r"^[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u26FF\u2700-\u27BF]+$"
        if not re.match(emoji_pattern, value):
            raise serializers.ValidationError(
                "Must be a valid emoji character."
            )
        return value

    def create(self, validated_data):
        """Create a reaction, ensuring the user has access to the message."""
        user = self.context["request"].user
        message = validated_data["message"]

        # user is a member of the bunch
        try:
            message.channel.bunch.members.get(user=user)
        except Member.DoesNotExist:
            raise serializers.ValidationError(
                "You must be a member of this bunch to react to messages."
            )

        validated_data["user"] = user
        return super().create(validated_data)


class MessageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    channel_id = serializers.UUIDField(source="channel.id", read_only=True)
    author_id = serializers.UUIDField(source="author.id", read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)
    reaction_counts = serializers.SerializerMethodField()
    reply_to_id = serializers.UUIDField(
        source="reply_to.id", read_only=True, allow_null=True
    )
    reply_count = serializers.IntegerField(read_only=True)

    # Nested serializer for the replied-to message preview
    reply_to_preview = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "url",
            "id",
            "content",
            "channel_id",
            "author_id",
            "reply_to_id",
            "reply_to_preview",
            "reply_count",
            "created_at",
            "edit_count",
            "updated_at",
            "deleted",
            "deleted_at",
            "reactions",
            "reaction_counts",
        ]
        read_only_fields = [
            "id",
            "channel_id",
            "author_id",
            "reply_to_id",
            "reply_to_preview",
            "reply_count",
            "created_at",
            "edit_count",
            "updated_at",
            "deleted",
            "deleted_at",
            "reactions",
            "reaction_counts",
        ]

    def get_reaction_counts(self, obj: Message) -> dict:
        """Get aggregated reaction counts by emoji."""
        from django.db.models import Count

        reaction_counts = (
            obj.reactions.values("emoji")
            .annotate(count=Count("emoji"))
            .order_by("-count")
        )
        return {item["emoji"]: item["count"] for item in reaction_counts}

    def get_reply_to_preview(self, obj: Message) -> dict | None:
        """Get a preview of the message being replied to."""
        if not obj.reply_to:
            return None

        return {
            "id": str(obj.reply_to.id),
            "content": obj.reply_to.content[:100] + "..."
            if len(obj.reply_to.content) > 100
            else obj.reply_to.content,
            "author": {
                "id": str(obj.reply_to.author.id),
                "username": obj.reply_to.author.user.username,
            },
            "created_at": obj.reply_to.created_at,
        }

    def get_url(self, obj: Message) -> str | None:
        request = self.context.get("request")
        if request is None:
            return None
        return request.build_absolute_uri(
            reverse(
                "bunch:bunch-message-detail",
                kwargs={
                    "bunch_id": obj.channel.bunch.id,
                    "id": obj.id,
                },
            )
        )
