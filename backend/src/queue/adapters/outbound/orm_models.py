"""Persistence adapter: the Django ORM models for services and queue entries."""

from __future__ import annotations

from django.db import models

from src.queue.domain.entities import STATUS_CHOICES


class ServiceModel(models.Model):
    business = models.ForeignKey(
        "businesses.BusinessModel",
        on_delete=models.CASCADE,
        related_name="services",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    ticket_prefix = models.CharField(max_length=2)
    avg_duration_sec = models.PositiveIntegerField(default=600)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "queue"
        db_table = "queue_service"
        verbose_name = "service"
        verbose_name_plural = "services"
        constraints = [
            models.UniqueConstraint(
                fields=["business", "ticket_prefix"], name="uniq_business_prefix"
            ),
        ]
        indexes = [
            models.Index(fields=["business", "is_active", "display_order"]),
        ]

    def __str__(self) -> str:
        return f"{self.business.name} / {self.ticket_prefix}"


class QueueEntryModel(models.Model):
    business = models.ForeignKey(
        "businesses.BusinessModel",
        on_delete=models.CASCADE,
        related_name="queue_entries",
    )
    service = models.ForeignKey(
        "queue.ServiceModel",
        on_delete=models.CASCADE,
        related_name="entries",
    )
    user = models.ForeignKey(
        "accounts.UserModel",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="queue_entries",
    )
    ticket_number = models.PositiveIntegerField()
    ticket_code = models.CharField(max_length=16)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="waiting")
    display_name = models.CharField(max_length=255, blank=True, default="")
    called_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    served_at = models.DateTimeField(null=True, blank=True)
    alert_sent = models.BooleanField(default=False)
    ticket_date = models.CharField(max_length=10, default="", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "queue"
        db_table = "queue_queueentry"
        verbose_name = "queue entry"
        verbose_name_plural = "queue entries"
        constraints = [
            models.UniqueConstraint(
                fields=["service", "ticket_number", "ticket_date"],
                name="uniq_ticket_per_day",
            ),
        ]
        indexes = [
            models.Index(fields=["service", "status", "ticket_number"]),
            models.Index(fields=["business", "created_at"]),
            models.Index(fields=["user", "status"]),
        ]
        ordering = ["created_at"]

    def __str__(self) -> str:
        return self.ticket_code
