"""Application use cases for the notifications feature."""

from __future__ import annotations

from dataclasses import dataclass

from src.notifications.domain.entities import KIND_IN_APP, Notification
from src.notifications.domain.exceptions import NotificationNotFound
from src.notifications.domain.ports import NotificationRepository, SmsSender
from src.shared.application.use_case import UseCase


@dataclass(frozen=True)
class SendNotificationCommand:
    user_id: int
    title: str
    body: str
    kind: str = KIND_IN_APP
    ref_kind: str = ""
    ref_id: int | None = None


class SendNotification(UseCase[SendNotificationCommand, Notification]):
    """Persist an in-app notification (email/SMS are handled by the senders)."""

    def __init__(self, notifications: NotificationRepository) -> None:
        self._notifications = notifications

    def execute(self, data: SendNotificationCommand) -> Notification:
        return self._notifications.add(
            user_id=data.user_id,
            title=data.title,
            body=data.body,
            kind=data.kind,
            ref_kind=data.ref_kind,
            ref_id=data.ref_id,
        )


@dataclass(frozen=True)
class SendSmsCommand:
    to_phone: str
    body: str


class SendSms(UseCase[SendSmsCommand, None]):
    """Best-effort outbound SMS via the ``SmsSender`` port (provider stub)."""

    def __init__(self, sms: SmsSender) -> None:
        self._sms = sms

    def execute(self, data: SendSmsCommand) -> None:
        self._sms.send(to_phone=data.to_phone, body=data.body)


class ListMyNotifications(UseCase[int, list[Notification]]):
    def __init__(self, notifications: NotificationRepository) -> None:
        self._notifications = notifications

    def execute(self, user_id: int) -> list[Notification]:
        return self._notifications.list_by_user(user_id, limit=50)


class UnreadCount(UseCase[int, int]):
    def __init__(self, notifications: NotificationRepository) -> None:
        self._notifications = notifications

    def execute(self, user_id: int) -> int:
        return self._notifications.unread_count(user_id)


class MarkRead(UseCase[tuple[int, int], Notification]):
    def __init__(self, notifications: NotificationRepository) -> None:
        self._notifications = notifications

    def execute(self, data: tuple[int, int]) -> Notification:
        notification_id, user_id = data
        notification = self._notifications.get_by_id(notification_id)
        if notification is None or notification.user_id != user_id:
            raise NotificationNotFound()
        if not notification.is_read:
            notification.is_read = True
            return self._notifications.mark_read(notification)
        return notification


class MarkAllRead(UseCase[int, int]):
    def __init__(self, notifications: NotificationRepository) -> None:
        self._notifications = notifications

    def execute(self, user_id: int) -> int:
        return self._notifications.mark_all_read(user_id)
