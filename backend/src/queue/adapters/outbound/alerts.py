"""Alerts adapter: implements the queue's ``NotificationGateway`` port by
calling the notifications feature's send use case.
"""

from __future__ import annotations

from src.queue.domain.ports import NotificationGateway


class NotificationsGatewayAdapter(NotificationGateway):
    def send(self, *, user_id: int, title: str, body: str,
             kind: str, ref_kind: str, ref_id: int) -> None:
        # Imported lazily to avoid a circular import at module load.
        from src.notifications.application.use_cases import SendNotificationCommand
        from src.notifications.container import container

        container().send_notification.execute(
            SendNotificationCommand(
                user_id=user_id,
                title=title,
                body=body,
                kind=kind,
                ref_kind=ref_kind,
                ref_id=ref_id,
            )
        )
