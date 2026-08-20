"""Composition root for the notifications feature."""

from __future__ import annotations

from functools import lru_cache

from django.conf import settings

from src.notifications.adapters.outbound.repositories import DjangoNotificationRepository
from src.notifications.adapters.outbound.sms import ConsoleSmsSender, ProviderSmsSender
from src.notifications.application.use_cases import (
    ListMyNotifications,
    MarkAllRead,
    MarkRead,
    SendNotification,
    SendSms,
    UnreadCount,
)
from src.notifications.domain.ports import SmsSender


class NotificationsContainer:
    def __init__(self) -> None:
        self.notifications = DjangoNotificationRepository()
        self.sms: SmsSender = self._build_sms_sender()

    @staticmethod
    def _build_sms_sender() -> SmsSender:
        provider = getattr(settings, "SMS_PROVIDER", "console")
        if provider == "provider":
            return ProviderSmsSender()
        return ConsoleSmsSender()

    @property
    def send_notification(self) -> SendNotification:
        return SendNotification(self.notifications)

    @property
    def send_sms(self) -> SendSms:
        return SendSms(self.sms)

    @property
    def list_my_notifications(self) -> ListMyNotifications:
        return ListMyNotifications(self.notifications)

    @property
    def unread_count(self) -> UnreadCount:
        return UnreadCount(self.notifications)

    @property
    def mark_read(self) -> MarkRead:
        return MarkRead(self.notifications)

    @property
    def mark_all_read(self) -> MarkAllRead:
        return MarkAllRead(self.notifications)


@lru_cache(maxsize=1)
def container() -> NotificationsContainer:
    return NotificationsContainer()
