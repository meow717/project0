"""Production settings: Postgres, MinIO (S3) storage, Redis cache, hardened.

Everything except the core Django vars is optional so a first deploy works on
card-free hosts (Render free tier, PythonAnywhere, etc.):
  - no DATABASE_URL  -> SQLite on disk
  - no REDIS_URL     -> local memory cache
  - no S3_*          -> local disk storage
"""

from __future__ import annotations

from .base import *  # noqa: F401,F403
from .base import BASE_DIR, MIDDLEWARE, env  # noqa: F401

DEBUG = False

# Serve compressed, hashed static files via WhiteNoise (right after security).
MIDDLEWARE = MIDDLEWARE.copy()
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

# Hosts/CSRF must be provided explicitly in production.
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# --- Database: Postgres, falling back to SQLite for card-free hosts ---------
_database_url = env("DATABASE_URL", default="")
if _database_url:
    DATABASES = {"default": env.db("DATABASE_URL")}
    DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=60)
    DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

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
