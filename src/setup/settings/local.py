import os
from pathlib import Path

from .base import *  # noqa: F401,F403

BASE_DIR = Path(__file__).resolve().parents[3]
DEBUG = os.getenv("DEBUG", "True").lower() in {"1", "true", "yes", "on"}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
