"""Persistence adapter: the Django ORM model for bookings."""

from __future__ import annotations

from django.db import models


class BookingModel(models.Model):
    business = models.ForeignKey(
        "businesses.BusinessModel",
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    service = models.ForeignKey(
        "queue.ServiceModel",
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    user = models.ForeignKey(
        "accounts.UserModel",
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    scheduled_at = models.DateTimeField()
    duration_sec = models.PositiveIntegerField(default=600)
    status = models.CharField(
        max_length=16,
        choices=(
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
            ("no_show", "No show"),
        ),
        default="pending",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "bookings"
        db_table = "bookings_booking"
        verbose_name = "booking"
        verbose_name_plural = "bookings"
        indexes = [
            models.Index(fields=["business", "scheduled_at"]),
            models.Index(fields=["user", "scheduled_at"]),
        ]

    def __str__(self) -> str:
        return f"Booking #{self.pk}"
