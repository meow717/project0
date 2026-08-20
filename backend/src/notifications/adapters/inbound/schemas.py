"""HTTP DTOs for the notifications feature."""

from __future__ import annotations

from datetime import datetime

from ninja import Schema


class NotificationOut(Schema):
    id: int
    title: str
    body: str
    kind: str
    ref_kind: str = ""
    ref_id: int | None = None
    is_read: bool
    created_at: datetime | None = None


class UnreadOut(Schema):
    unread_count: int
