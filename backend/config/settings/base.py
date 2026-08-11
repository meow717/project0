"""
Base Django settings shared across every environment.

Environment-specific overrides live in ``dev.py`` and ``prod.py``.
All tunable values are read from the environment via ``django-environ`` so the
same image can run anywhere (12-factor). See ``.env.example``.
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import environ

# backend/ -> project root (config/settings/base.py -> parents[2])
BASE_DIR = Path(__file__).resolve().parents[2]

env = environ.Env()
# Read a local .env if present (dev convenience; in prod vars come from Coolify).
environ.Env.read_env(BASE_DIR / ".env")

# --------------------------------------------------------------------------- #
# Core
# --------------------------------------------------------------------------- #
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="dev-insecure-secret-key-change-me-in-production-0123456789",
)
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    # Unfold must precede django.contrib.admin to theme it.
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "corsheaders",
    # local features (hexagon)
    "src.accounts",
]

# django-unfold admin theme
UNFOLD = {
    "SITE_TITLE": "Template Admin",
    "SITE_HEADER": "Template Admin",
    "SITE_SUBHEADER": "Backend administration",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise is added in prod.py (static is served by runserver in dev).
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --------------------------------------------------------------------------- #
# Auth
# --------------------------------------------------------------------------- #
AUTH_USER_MODEL = "accounts.UserModel"

# Argon2 first so both the API (via the PasswordHasher port) and the Django
# admin use the same modern hashing scheme.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Default admin superuser, auto-provisioned on `migrate` / `ensure_admin`.
ADMIN_EMAIL = env("ADMIN_EMAIL", default="admin@admin.com")
ADMIN_PASSWORD = env("ADMIN_PASSWORD", default="admin123")
ADMIN_FULL_NAME = env("ADMIN_FULL_NAME", default="Administrator")

# --------------------------------------------------------------------------- #
# JWT (consumed by src/shared/infrastructure/auth.py + the token adapter)
# --------------------------------------------------------------------------- #
JWT = {
    "SECRET": env("JWT_SECRET", default=SECRET_KEY),
    "ALGORITHM": env("JWT_ALGORITHM", default="HS256"),
    "ACCESS_TTL": timedelta(minutes=env.int("JWT_ACCESS_TTL_MIN", default=15)),
    "REFRESH_TTL": timedelta(days=env.int("JWT_REFRESH_TTL_DAYS", default=7)),
    "ISSUER": env("JWT_ISSUER", default="karkh-backend"),
}

# --------------------------------------------------------------------------- #
# i18n / tz
# --------------------------------------------------------------------------- #
LANGUAGE_CODE = "en-us"
TIME_ZONE = env("DJANGO_TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------- #
# Static / media (STORAGES is overridden per environment)
# --------------------------------------------------------------------------- #
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------------------------------- #
# CORS (the Next.js frontend)
# --------------------------------------------------------------------------- #
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:3000", "http://127.0.0.1:3000"],
)
CORS_ALLOW_CREDENTIALS = True
