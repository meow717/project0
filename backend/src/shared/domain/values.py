"""Shared value objects (pure Python, no Django)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time


@dataclass(frozen=True)
class Page[T]:
    """Pagination result: items on this page plus the total across pages."""

    items: list[T]
    total: int
    page: int
    page_size: int


@dataclass(frozen=True)
class BusinessHours:
    """Local operating hours for a business (time-of-day, no date)."""

    opens_at: time
    closes_at: time

    def contains(self, local_dt: datetime) -> bool:
        """True if ``local_dt`` falls within the working window (midnight wraps)."""
        t = local_dt.time()
        if self.opens_at < self.closes_at:
            return self.opens_at <= t <= self.closes_at
        # Overnight window (e.g. 22:00 -> 06:00).
        return t >= self.opens_at or t <= self.closes_at


# Kept as a placeholder for future shared value objects (e.g. money, addresses).
__all__: list[str] = ["Page", "BusinessHours"]
