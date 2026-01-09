"""
ASGI config for bunch project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orchard.settings")

django_asgi_app = get_asgi_application()

from orchard.middleware import SupabaseChannelsAuthMiddleware
from orchard.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": SupabaseChannelsAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        ),
    }
)
