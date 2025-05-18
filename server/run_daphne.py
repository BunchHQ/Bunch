import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "orchard.settings"
)

# Initialize Django
import django

django.setup()

if __name__ == "__main__":
    from daphne.cli import CommandLineInterface

    CommandLineInterface().run(
        [
            "orchard.asgi:application",
            "-b",
            "0.0.0.0",
            "-p",
            "8000",
        ]
    )
