from django.urls import re_path

from bunch.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(
        r"ws/bunch/$",
        ChatConsumer.as_asgi(),  # pyright: ignore
    ),
]
