"""Re-export ORM models for Django autodiscovery / migrations."""

from src.notifications.adapters.outbound.orm_models import NotificationModel

__all__ = ["NotificationModel"]
