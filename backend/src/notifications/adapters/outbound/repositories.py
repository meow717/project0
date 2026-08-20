"""Persistence adapter: maps Notification ORM rows to/from the entity."""

from __future__ import annotations

from src.notifications.adapters.outbound.orm_models import NotificationModel
from src.notifications.domain.entities import Notification
from src.notifications.domain.ports import NotificationRepository


class DjangoNotificationRepository(NotificationRepository):
    def add(self, *, user_id, title, body, kind, ref_kind, ref_id) -> Notification:
        row = NotificationModel.objects.create(
            user_id=user_id,
            title=title,
            body=body,
            kind=kind,
            ref_kind=ref_kind,
            ref_id=ref_id,
        )
        return self._to_entity(row)

    def list_by_user(self, user_id: int, limit: int) -> list[Notification]:
        rows = NotificationModel.objects.filter(user_id=user_id).order_by(
            "-created_at"
        )[:limit]
        return [self._to_entity(r) for r in rows]

    def unread_count(self, user_id: int) -> int:
        return NotificationModel.objects.filter(user_id=user_id, is_read=False).count()

    def get_by_id(self, notification_id: int) -> Notification | None:
        row = NotificationModel.objects.filter(pk=notification_id).first()
        return self._to_entity(row) if row else None

    def mark_read(self, notification: Notification) -> Notification:
        NotificationModel.objects.filter(pk=notification.id).update(is_read=True)
        return self._to_entity(NotificationModel.objects.get(pk=notification.id))

    def mark_all_read(self, user_id: int) -> int:
        return NotificationModel.objects.filter(user_id=user_id, is_read=False).update(
            is_read=True
        )

    @staticmethod
    def _to_entity(row: NotificationModel) -> Notification:
        return Notification(
            id=row.pk,
            user_id=row.user_id,
            title=row.title,
            body=row.body,
            kind=row.kind,
            ref_kind=row.ref_kind,
            ref_id=row.ref_id,
            is_read=row.is_read,
            created_at=row.created_at,
        )
