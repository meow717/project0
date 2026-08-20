"""Booking domain entities (pure Python)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.shared.domain.entity import Entity

BOOKING_PENDING = "pending"
BOOKING_CONFIRMED = "confirmed"
BOOKING_COMPLETED = "completed"
BOOKING_CANCELLED = "cancelled"
BOOKING_NO_SHOW = "no_show"

BOOKING_STATUS_CHOICES = (
    (BOOKING_PENDING, "Pending"),
    (BOOKING_CONFIRMED, "Confirmed"),
    (BOOKING_COMPLETED, "Completed"),
    (BOOKING_CANCELLED, "Cancelled"),
    (BOOKING_NO_SHOW, "No show"),
)

# Statuses a customer may cancel.
CUSTOMER_CANCELLABLE = (BOOKING_PENDING, BOOKING_CONFIRMED)


@dataclass(kw_only=True)
class Booking(Entity):
    business_id: int
    service_id: int
    user_id: int
    scheduled_at: datetime
    duration_sec: int
    status: str = BOOKING_PENDING
    notes: str = ""
