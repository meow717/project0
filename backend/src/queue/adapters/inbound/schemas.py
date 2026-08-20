"""HTTP DTOs for the queue feature."""

from __future__ import annotations

from datetime import datetime

from ninja import Schema
from pydantic import Field


class ServiceCreateIn(Schema):
    name: str = Field(min_length=1, max_length=255)
    ticket_prefix: str = Field(min_length=1, max_length=2)
    description: str = Field(default="", max_length=2000)
    avg_duration_sec: int = Field(default=600, ge=1)


class ServiceUpdateIn(Schema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    avg_duration_sec: int | None = Field(default=None, ge=1)


class ServiceOut(Schema):
    id: int
    business_id: int
    name: str
    description: str = ""
    ticket_prefix: str
    avg_duration_sec: int
    is_active: bool = True


class QueueEntryOut(Schema):
    id: int
    business_id: int
    service_id: int
    ticket_code: str
    ticket_number: int
    status: str
    position: int = 0
    est_wait_seconds: int = 0
    display_name: str | None = None
    created_at: datetime | None = None
    called_at: datetime | None = None
    started_at: datetime | None = None
    served_at: datetime | None = None


class WaitOut(Schema):
    position: int
    est_seconds: int


class LiveSnapshotOut(Schema):
    business_id: int
    generated_at: datetime
    crowd_level: str
    services: list[ServiceLiveStatusOut]


class ServiceLiveStatusOut(Schema):
    service_id: int
    name: str
    prefix: str
    current_number: str | None = None
    waiting_count: int = 0
    est_wait_min: int = 0
    state: str = "closed"


class WalkInIn(Schema):
    service_id: int
    display_name: str | None = Field(default=None, max_length=255)


class CallIn(Schema):
    entry_id: int


class ServedPerDayOut(Schema):
    date: str
    count: int


class ServedPerHourOut(Schema):
    hour: int
    count: int


class ServiceStatOut(Schema):
    service_id: int
    name: str
    served: int
    avg_wait_min: int


class StatsReportOut(Schema):
    served_per_day: list[ServedPerDayOut]
    served_per_hour: list[ServedPerHourOut]
    by_service: list[ServiceStatOut]
