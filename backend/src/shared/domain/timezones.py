"""Business-timezone helpers (pure Python, stdlib only)."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.shared.domain.exceptions import ValidationError


def resolve_zone(iana_name: str) -> ZoneInfo:
    """Validate an IANA timezone name, raising a domain error if unknown."""
    try:
        return ZoneInfo(iana_name)
    except ZoneInfoNotFoundError as exc:
        raise ValidationError(f"Unknown timezone: {iana_name}") from exc


def local_day(dt: datetime, iana_name: str) -> str:
    """Return the calendar date of ``dt`` in the given IANA timezone (ISO)."""
    return dt.astimezone(resolve_zone(iana_name)).date().isoformat()
