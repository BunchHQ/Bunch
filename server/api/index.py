import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orchard.settings")

from orchard.asgi import application

app = application
