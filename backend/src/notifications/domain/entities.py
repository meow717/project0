"""Notification domain entities (pure Python)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.shared.domain.entity import Entity

KIND_IN_APP = "in_app"
KIND_EMAIL = "email"
KIND_SMS = "sms"


@dataclass(kw_only=True)
class Notification(Entity):
    user_id: int
    title: str
    body: str
    kind: str = KIND_IN_APP
    ref_kind: str = ""  # "queue" | "booking" | ...
    ref_id: int | None = None
    is_read: bool = False
    sent_at: datetime | None = None
