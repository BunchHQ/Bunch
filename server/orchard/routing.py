from django.urls import re_path
from bunch.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(
        r"ws/bunch/(?P<bunch_id>[^/]+)/channel/(?P<channel_id>[^/]+)/$",
        ChatConsumer.as_asgi(),
    ),
]
