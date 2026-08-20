"""Queue domain entities and value objects (pure Python)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from src.shared.domain.entity import Entity


# --------------------------------------------------------------------------- #
# Service (a queue line offered by a business)
# --------------------------------------------------------------------------- #
@dataclass(kw_only=True)
class Service(Entity):
    business_id: int
    name: str
    ticket_prefix: str
    description: str = ""
    avg_duration_sec: int = 600
    is_active: bool = True
    display_order: int = 0


# --------------------------------------------------------------------------- #
# QueueEntry (a ticket in a service queue)
# --------------------------------------------------------------------------- #
STATUS_WAITING = "waiting"
STATUS_CALLED = "called"
STATUS_IN_PROGRESS = "in_progress"
STATUS_SERVED = "served"
STATUS_NO_SHOW = "no_show"
STATUS_CANCELLED = "cancelled"

ACTIVE_STATUSES = (STATUS_WAITING, STATUS_CALLED, STATUS_IN_PROGRESS)

STATUS_CHOICES = (
    (STATUS_WAITING, "Waiting"),
    (STATUS_CALLED, "Called"),
    (STATUS_IN_PROGRESS, "In progress"),
    (STATUS_SERVED, "Served"),
    (STATUS_NO_SHOW, "No show"),
    (STATUS_CANCELLED, "Cancelled"),
)


@dataclass(kw_only=True)
class QueueEntry(Entity):
    business_id: int
    service_id: int
    ticket_number: int
    ticket_code: str
    status: str = STATUS_WAITING
    user_id: int | None = None
    display_name: str | None = None
    called_at: datetime | None = None
    started_at: datetime | None = None
    served_at: datetime | None = None
    alert_sent: bool = False
    ticket_date: str = field(default="")  # business-local calendar date (ISO)


# --------------------------------------------------------------------------- #
# Value objects
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class TicketCode:
    prefix: str
    number: int

    def __str__(self) -> str:
        return f"{self.prefix}-{self.number:03d}"


@dataclass(frozen=True)
class WaitEstimate:
    entry_id: int
    position: int
    est_seconds: int


@dataclass(frozen=True)
class ServiceLiveStatus:
    service_id: int
    name: str
    prefix: str
    current_number: str | None
    waiting_count: int
    est_wait_min: int
    state: str  # "closed" | "idle" | "busy"


@dataclass(frozen=True)
class QueueSnapshot:
    business_id: int
    generated_at: datetime
    crowd_level: str  # low | medium | high
    services: list[ServiceLiveStatus]


@dataclass(frozen=True)
class ServedPerDay:
    date: str
    count: int


@dataclass(frozen=True)
class ServedPerHour:
    hour: int
    count: int


@dataclass(frozen=True)
class ServiceStat:
    service_id: int
    name: str
    served: int
    avg_wait_min: int


@dataclass(frozen=True)
class StatsReport:
    """Typed staff-dashboard statistics (replaces the plain dict)."""

    served_per_day: list[ServedPerDay]
    served_per_hour: list[ServedPerHour]
    by_service: list[ServiceStat]
