"""Re-export the ORM model for Django autodiscovery / migrations."""

from src.businesses.adapters.outbound.orm_models import BusinessModel

__all__ = ["BusinessModel"]
