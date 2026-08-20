"""Django admin (themed by django-unfold) for businesses."""

from __future__ import annotations

from django.contrib import admin
from unfold.admin import ModelAdmin

from src.businesses.models import BusinessModel


@admin.register(BusinessModel)
class BusinessAdmin(ModelAdmin):
    list_display = ("id", "name", "slug", "area", "category", "timezone", "is_active", "created_by", "created_at")
    list_filter = ("is_active", "area", "category", "timezone")
    search_fields = ("name", "slug", "address", "area", "category")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
