"""Persistence adapter: the Django ORM model for notifications."""

from __future__ import annotations

from django.db import models


class NotificationModel(models.Model):
    user = models.ForeignKey(
        "accounts.UserModel",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    kind = models.CharField(
        max_length=16,
        choices=(
            ("in_app", "In-app"),
            ("email", "Email"),
            ("sms", "SMS"),
        ),
        default="in_app",
    )
    ref_kind = models.CharField(max_length=16, blank=True, default="")
    ref_id = models.IntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "notifications"
        db_table = "notifications_notification"
        verbose_name = "notification"
        verbose_name_plural = "notifications"
        indexes = [
            models.Index(fields=["user", "is_read", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.title
