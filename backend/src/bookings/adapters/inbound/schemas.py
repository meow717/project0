"""HTTP DTOs for the bookings feature."""

from __future__ import annotations

from datetime import datetime

from ninja import Schema
from pydantic import Field


class BookingCreateIn(Schema):
    business_id: int
    service_id: int
    scheduled_at: datetime
    notes: str = Field(default="", max_length=2000)


class BookingOut(Schema):
    id: int
    business_id: int
    service_id: int
    service_name: str = ""
    scheduled_at: datetime
    duration_sec: int
    status: str
    notes: str = ""


class BookingStatusIn(Schema):
    status: str
