"""Re-export ORM models for Django autodiscovery / migrations."""

from src.bookings.adapters.outbound.orm_models import BookingModel

__all__ = ["BookingModel"]
