from typing import override

from django.apps import AppConfig


class BunchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bunch"

    @override
    def ready(self) -> None:
        import bunch.signals  # noqa

        return super().ready()
