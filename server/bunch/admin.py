from django.contrib import admin
from django.utils.html import format_html

from bunch.models import Bunch, Channel, Member, Message


@admin.register(Bunch)
class BunchAdmin(admin.ModelAdmin):
    list_display: tuple[str, ...] = (
        "id",
        "name",
        "owner",
        "member_count",
        "channel_count",
        "is_private",
        "created_at",
        "show_icon",
    )
    list_filter: tuple[str, ...] = (
        "is_private",
        "created_at",
    )
    search_fields = (
        "name",
        "description",
        "owner__username",
    )
    readonly_fields: tuple[str, ...] = (
        "id",
        "created_at",
        "updated_at",
        "show_channels",
        "show_members",
        "member_count",
        "channel_count",
    )

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "id",
                    "name",
                    "description",
                    "owner",
                    "icon",
                )
            },
        ),
        (
            "Settings",
            {"fields": ("is_private", "invite_code")},
        ),
        (
            "Related Objects",
            {
                "fields": ("show_channels", "show_members"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def member_count(self, obj):
        return obj.members.count()

    member_count.short_description = "Members"

    def channel_count(self, obj):
        return obj.channels.count()

    channel_count.short_description = "Channels"

    def show_icon(self, obj):
        if obj.icon:
            return format_html(
                '<img src="{}" width="50" height="50" />',
                obj.icon.url,
            )
        return "No icon"

    show_icon.short_description = "Icon"

    def show_channels(self, obj):
        return format_html(
            "<br>".join(
                f"{channel.name} ({channel.type})"
                for channel in obj.channels.all()
            )
        )

    show_channels.short_description = "Channels"

    def show_members(self, obj):
        return format_html(
            "<br>".join(
                f"{member.user.username} ({member.role})"
                for member in obj.members.all()
            )
        )

    show_members.short_description = "Members"


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display: tuple[str, ...] = (
        "id",
        "user",
        "bunch",
        "role",
        "joined_at",
        "nickname",
    )
    list_filter: tuple[str, ...] = (
        "role",
        "joined_at",
        "bunch",
    )
    search_fields: tuple[str, ...] = (
        "user__username",
        "bunch__name",
        "nickname",
    )
    raw_id_fields: tuple[str, ...] = ("user", "bunch")

    readonly_fields: tuple[str, ...] = (
        "id",
        "bunch_memberships",
        "owned_bunches",
        "joined_at",
    )

    fieldsets = (
        (
            "Membership Information",
            {"fields": ("id", "user", "bunch", "role")},
        ),
        (
            "Related Objects",
            {
                "fields": (
                    "bunch_memberships",
                    "owned_bunches",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Additional Information",
            {"fields": ("nickname", "joined_at")},
        ),
    )

    def bunch_memberships(self, obj: Member):
        return format_html(
            "<br>".join(
                f"{membership.bunch.name}"
                for membership in obj.user.bunch_memberships.all()
            )
        )

    def owned_bunches(self, obj: Member):
        return format_html(
            "<br>".join(
                f"{bunch.name}"
                for bunch in obj.user.owned_bunches.all()
            )
        )


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display: tuple[str, ...] = (
        "name",
        "bunch",
        "type",
        "is_private",
        "position",
        "created_at",
    )
    list_filter: tuple[str, ...] = (
        "type",
        "is_private",
        "created_at",
        "bunch",
    )
    search_fields: tuple[str, ...] = (
        "name",
        "description",
        "bunch__name",
    )
    raw_id_fields: tuple[str, ...] = ("bunch",)

    fieldsets = (
        (
            "Channel Information",
            {
                "fields": (
                    "name",
                    "bunch",
                    "type",
                    "description",
                )
            },
        ),
        (
            "Settings",
            {"fields": ("is_private", "position")},
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )
    readonly_fields: tuple[str, ...] = ("created_at",)

    list_editable: tuple[str, ...] = ("position",)
    ordering: tuple[str, ...] = ("bunch", "position")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display: tuple[str, ...] = (
        "content",
        "channel",
        "author",
        "created_at",
        "edit_count",
        "deleted",
    )
    list_filter: tuple[str, ...] = (
        "channel",
        "author",
        "created_at",
        "deleted",
    )
    search_fields: tuple[str, ...] = (
        "content",
        "channel__name",
        "author__username",
    )
    raw_id_fields: tuple[str, ...] = ("channel", "author")

    fieldsets = (
        (
            "Message Information",
            {
                "fields": (
                    "content",
                    "channel",
                    "author",
                    "edit_count",
                    "deleted",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "deleted_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )
    readonly_fields: tuple[str, ...] = (
        "created_at",
        "updated_at",
        "deleted_at",
        "edit_count",
        "deleted",
        "channel",
        "author",
    )

    list_editable: tuple[str, ...] = ()
    ordering: tuple[str, ...] = ("channel", "created_at")
