"""Driven ports for the notifications feature."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.notifications.domain.entities import Notification


class NotificationRepository(ABC):
    @abstractmethod
    def add(self, *, user_id: int, title: str, body: str, kind: str,
            ref_kind: str, ref_id: int | None) -> Notification: ...

    @abstractmethod
    def list_by_user(self, user_id: int, limit: int) -> list[Notification]: ...

    @abstractmethod
    def unread_count(self, user_id: int) -> int: ...

    @abstractmethod
    def get_by_id(self, notification_id: int) -> Notification | None: ...

    @abstractmethod
    def mark_read(self, notification: Notification) -> Notification: ...

    @abstractmethod
    def mark_all_read(self, user_id: int) -> int: ...


class EmailSender(ABC):
    """Outbound email delivery (console backend in dev, SMTP in prod)."""

    @abstractmethod
    def send(self, *, to_email: str, subject: str, body: str) -> None: ...


class SmsSender(ABC):
    """Outbound SMS delivery (console no-op in dev, provider in prod)."""

    @abstractmethod
    def send(self, *, to_phone: str, body: str) -> None: ...
