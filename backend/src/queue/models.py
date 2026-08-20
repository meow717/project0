"""Re-export ORM models for Django autodiscovery / migrations."""

from src.queue.adapters.outbound.orm_models import QueueEntryModel, ServiceModel

__all__ = ["QueueEntryModel", "ServiceModel"]
