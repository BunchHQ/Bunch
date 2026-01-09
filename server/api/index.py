import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orchard.settings")

from orchard.wsgi import application

app = application
