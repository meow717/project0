"""Notification domain exceptions."""

from __future__ import annotations

from src.shared.domain.exceptions import NotFoundError


class NotificationNotFound(NotFoundError):
    code = "notification_not_found"
