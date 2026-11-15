import os

import dj_database_url

from .base import *  # noqa: F401,F403,F405

DEBUG = False
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

DATABASE_URL = os.environ["DATABASE_URL"]
DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

if render_hostname:
    CSRF_TRUSTED_ORIGINS = [f"https://{render_hostname}"]
CSRF_TRUSTED_ORIGINS += [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
