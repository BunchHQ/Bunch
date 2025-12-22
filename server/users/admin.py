from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as BaseUserAdmin,
)
from django.contrib.auth.models import Group

from users.models import User


class UserAdmin(BaseUserAdmin):
    fieldsets = tuple(
        (name, data)
        if name != "Personal info"
        else (
            name,
            {
                "fields": data["fields"]
                + (
                    "avatar",
                    "status",
                    "bio",
                    "theme_preference",
                    "color",
                    "pronoun",
                )  # type: ignore
            },
        )
        for name, data in BaseUserAdmin.fieldsets or []
    )
    list_display: tuple = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    list_filter: tuple = ("is_staff", "is_active")
    search_fields: tuple = (
        "email",
        "first_name",
        "last_name",
        "username",
        "bio",
        "status",
    )
    ordering: tuple = ("date_joined",)


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
