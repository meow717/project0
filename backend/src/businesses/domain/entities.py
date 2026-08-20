"""Business domain entities and value objects (pure Python)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time

from src.shared.domain.entity import Entity
from src.shared.domain.values import BusinessHours


@dataclass(kw_only=True)
class Business(Entity):
    name: str
    slug: str
    description: str = ""
    area: str = ""
    category: str = ""
    address: str = ""
    phone: str = ""
    timezone: str = "Asia/Riyadh"
    opens_at: time = time(9, 0)
    closes_at: time = time(17, 0)
    logo_url: str | None = None
    is_active: bool = True
    created_by: int | None = None

    @property
    def hours(self) -> BusinessHours:
        return BusinessHours(opens_at=self.opens_at, closes_at=self.closes_at)
