"""Django admin (themed by django-unfold).

Passwords are read-only here — create the admin via `ensure_admin` /
`createsuperuser`, and users via the API. This avoids storing a plaintext
password through the admin form.
"""

from __future__ import annotations

from django.contrib import admin
from unfold.admin import ModelAdmin

from src.accounts.models import UserModel


@admin.register(UserModel)
class UserAdmin(ModelAdmin):
    list_display = (
        "id",
        "email",
        "full_name",
        "role",
        "business",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "role")
    search_fields = ("email", "full_name")
    ordering = ("id",)
    readonly_fields = ("password", "last_login", "date_joined", "updated_at")
