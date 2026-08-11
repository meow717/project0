"""Development settings: SQLite, local filesystem storage, in-memory cache."""

from __future__ import annotations

from .base import *  # noqa: F401,F403
from .base import BASE_DIR, env  # noqa: F401

DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Local filesystem media + Django's static finder/whitenoise for static.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# Cache is optional in dev: in-memory by default, real Redis if REDIS_URL is set.
_redis_url = env("REDIS_URL", default="")
if _redis_url:
    CACHES = {"default": {"BACKEND": "django_redis.cache.RedisCache", "LOCATION": _redis_url}}
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# Allow any localhost origin while developing.
CORS_ALLOW_ALL_ORIGINS = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
