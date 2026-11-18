import os

import dj_database_url

from .base import *  # noqa: F401,F403
from .base import BASE_DIR

DEBUG = False
STATIC_ROOT = BASE_DIR / "staticfiles"
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
allowed_hosts = {
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "").split(",")
    if host.strip()
}
if render_hostname:
    allowed_hosts.add(render_hostname)
ALLOWED_HOSTS = sorted(allowed_hosts)
if not ALLOWED_HOSTS:
    raise RuntimeError("ALLOWED_HOSTS must contain at least one host in production.")

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
if render_hostname:
    CSRF_TRUSTED_ORIGINS.append(f"https://{render_hostname}")

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "organizador_tarefas"),
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.environ["POSTGRES_PASSWORD"],
            "HOST": os.getenv("POSTGRES_HOST", "postgres"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
