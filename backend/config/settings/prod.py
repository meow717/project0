"""Production settings: Postgres, MinIO (S3) storage, Redis cache, hardened.

Redis/S3/MinIO are optional: if their env vars are absent the app falls back
to the local memory cache and local file storage so a first deploy on Render's
free tier works with just a Postgres URL.
"""

from __future__ import annotations

from .base import *  # noqa: F401,F403
from .base import MIDDLEWARE, env  # noqa: F401

DEBUG = False

# Serve compressed, hashed static files via WhiteNoise (right after security).
MIDDLEWARE = MIDDLEWARE.copy()
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

# Hosts/CSRF must be provided explicitly in production.
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# --- Database: Postgres -----------------------------------------------------
# DATABASE_URL is required in prod (Render provides it via the Postgres add-on).
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=60)
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True

# --- Cache: Redis (optional; local memory cache if REDIS_URL is unset) ------
_redis_url = env("REDIS_URL", default="")
if _redis_url:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": _redis_url,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# --- Storage: MinIO / S3-compatible (optional; local disk if unset) ---------
_s3_endpoint = env("S3_ENDPOINT_URL", default="")
if _s3_endpoint:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "bucket_name": env("S3_BUCKET_NAME"),
                "endpoint_url": _s3_endpoint,
                "access_key": env("S3_ACCESS_KEY"),
                "secret_key": env("S3_SECRET_KEY"),
                "region_name": env("S3_REGION", default="us-east-1"),
                "addressing_style": "path",  # required by MinIO
                "file_overwrite": False,
                "querystring_auth": env.bool("S3_QUERYSTRING_AUTH", default=True),
                "url_protocol": env("S3_URL_PROTOCOL", default="https:"),
            },
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }

# --- Security ---------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=2592000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# --- Email: SMTP required in prod (console backend is dev-only) --------------
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
