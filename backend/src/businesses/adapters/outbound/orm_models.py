"""Persistence adapter: the Django ORM model for businesses."""

from __future__ import annotations

from django.db import models


class BusinessModel(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    area = models.CharField(max_length=64, blank=True, default="")
    category = models.CharField(max_length=64, blank=True, default="")
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=64, blank=True)
    timezone = models.CharField(max_length=64, default="Asia/Riyadh")
    opens_at = models.TimeField(default="09:00")
    closes_at = models.TimeField(default="17:00")
    logo = models.CharField(max_length=500, blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        "accounts.UserModel",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_businesses",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "businesses"
        db_table = "businesses_business"
        verbose_name = "business"
        verbose_name_plural = "businesses"
        indexes = [
            models.Index(fields=["is_active", "slug"]),
            models.Index(fields=["created_by"]),
        ]

    def __str__(self) -> str:
        return self.name
