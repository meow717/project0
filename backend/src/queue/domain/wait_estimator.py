"""Wait-time estimation (pure domain logic).

The average service duration per service is an exponential moving average (EMA,
alpha = 0.2) of the times of completed (served) entries. A waiting entry's
estimated remaining wait is the sum of expected durations of entries ahead of
it plus the time already spent on the currently in-progress entry.
"""

from __future__ import annotations

from datetime import UTC, datetime

from src.queue.domain.entities import (
    STATUS_IN_PROGRESS,
    STATUS_WAITING,
    QueueEntry,
    Service,
)

EMA_ALPHA = 0.2


def update_avg_duration(current: int, served_duration_sec: int) -> int:
    """Blend a new observed duration into the EMA, returning a rounded int."""
    if served_duration_sec <= 0:
        return current
    return max(1, round(EMA_ALPHA * served_duration_sec + (1 - EMA_ALPHA) * current))


def _now() -> datetime:
    return datetime.now(UTC)


def estimate_wait(
    entries: list[QueueEntry],
    services: dict[int, Service],
    now: datetime | None = None,
) -> int:
    """Total estimated seconds until the last *waiting* entry is served.

    ``entries`` must be ordered oldest-first. An in-progress entry contributes
    its remaining time (avg_duration - elapsed); each waiting entry ahead
    contributes its service's avg_duration.
    """
    now = now or _now()
    total = 0.0
    for entry in entries:
        service = services.get(entry.service_id)
        avg = service.avg_duration_sec if service else 600
        if entry.status == STATUS_IN_PROGRESS and entry.started_at:
            elapsed = (now - entry.started_at).total_seconds()
            total += max(0.0, avg - elapsed)
        elif entry.status == STATUS_WAITING:
            total += avg
    return int(total)


def position_of(entry: QueueEntry, entries: list[QueueEntry]) -> int:
    """1-based position of ``entry`` among the (ordered) waiting list."""
    for i, other in enumerate(entries, start=1):
        if other.id == entry.id:
            return i
    return 0
