"""Driven ports for the bookings feature."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from src.bookings.domain.entities import Booking
from src.shared.domain.values import BusinessHours


class BookingRepository(ABC):
    @abstractmethod
    def get_by_id(self, booking_id: int) -> Booking | None: ...

    @abstractmethod
    def add(self, *, business_id: int, service_id: int, user_id: int,
            scheduled_at: datetime, duration_sec: int, notes: str) -> Booking: ...

    @abstractmethod
    def list_by_user(self, user_id: int) -> list[Booking]: ...

    @abstractmethod
    def list_by_business_and_date(self, business_id: int, day: str) -> list[Booking]: ...

    @abstractmethod
    def update(self, booking: Booking) -> Booking: ...

    @abstractmethod
    def overlapping(self, business_id: int, service_id: int,
                    start: datetime, end: datetime) -> Booking | None: ...


class BusinessReader(ABC):
    """Read-only view of a business (timezone + hours) for bookings."""

    @abstractmethod
    def get_hours(self, business_id: int) -> tuple[str, BusinessHours]: ...

