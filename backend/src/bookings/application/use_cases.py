"""Application use cases for the bookings feature."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from src.bookings.domain.entities import (
    BOOKING_CANCELLED,
    BOOKING_COMPLETED,
    BOOKING_CONFIRMED,
    BOOKING_NO_SHOW,
    BOOKING_PENDING,
    CUSTOMER_CANCELLABLE,
    Booking,
)
from src.bookings.domain.exceptions import (
    BookingConflict,
    BookingNotFound,
    InvalidBookingStatus,
    OutsideWorkingHours,
)
from src.bookings.domain.ports import BookingRepository, BusinessReader
from src.queue.domain.ports import ServiceReader
from src.shared.application.use_case import UseCase
from src.shared.domain.exceptions import PermissionDeniedError
from src.shared.domain.ports import Clock
from src.shared.domain.timezones import resolve_zone


@dataclass(frozen=True)
class CreateBookingCommand:
    business_id: int
    service_id: int
    user_id: int
    scheduled_at: datetime
    notes: str = ""


class CreateBooking(UseCase[CreateBookingCommand, Booking]):
    def __init__(
        self,
        bookings: BookingRepository,
        services: ServiceReader,
        businesses: BusinessReader,
        clock: Clock,
    ) -> None:
        self._bookings = bookings
        self._services = services
        self._businesses = businesses
        self._clock = clock

    def execute(self, data: CreateBookingCommand) -> Booking:
        service = self._services.get_by_id(data.service_id)
        if service is None or service.business_id != data.business_id:
            raise BookingNotFound("Service not found in this business")

        scheduled = data.scheduled_at
        if scheduled.tzinfo is None:
            scheduled = scheduled.replace(tzinfo=UTC)

        if scheduled <= self._clock.now():
            raise OutsideWorkingHours("Booking must be in the future")

        # Business hours check.
        tz_name, hours = self._businesses.get_hours(data.business_id)
        tz = resolve_zone(tz_name)
        local = scheduled.astimezone(tz)
        if not hours.contains(local):
            raise OutsideWorkingHours("Outside business working hours")

        duration = service.avg_duration_sec
        end = scheduled + timedelta(seconds=duration)
        if self._bookings.overlapping(data.business_id, data.service_id, scheduled, end):
            raise BookingConflict("Time slot already booked")

        return self._bookings.add(
            business_id=data.business_id,
            service_id=data.service_id,
            user_id=data.user_id,
            scheduled_at=scheduled,
            duration_sec=duration,
            notes=data.notes.strip(),
        )


class ListMyBookings(UseCase[int, list[Booking]]):
    def __init__(self, bookings: BookingRepository) -> None:
        self._bookings = bookings

    def execute(self, user_id: int) -> list[Booking]:
        return self._bookings.list_by_user(user_id)


class CancelBooking(UseCase[tuple[int, int], Booking]):
    def __init__(self, bookings: BookingRepository, clock: Clock) -> None:
        self._bookings = bookings
        self._clock = clock

    def execute(self, data: tuple[int, int]) -> Booking:
        booking_id, user_id = data
        booking = self._bookings.get_by_id(booking_id)
        if booking is None or booking.user_id != user_id:
            raise BookingNotFound()
        if booking.status not in CUSTOMER_CANCELLABLE:
            raise InvalidBookingStatus("This booking can no longer be cancelled")
        booking.status = "cancelled"
        return self._bookings.update(booking)


class ListBusinessBookings(UseCase[tuple[int, str], list[Booking]]):
    def __init__(self, bookings: BookingRepository) -> None:
        self._bookings = bookings

    def execute(self, data: tuple[int, str]) -> list[Booking]:
        business_id, day = data
        return self._bookings.list_by_business_and_date(business_id, day)


class SetBookingStatus(UseCase[tuple[int, int, str], Booking]):
    """Staff sets the status of a booking (confirm/complete/no_show)."""

    def __init__(self, bookings: BookingRepository, clock: Clock) -> None:
        self._bookings = bookings
        self._clock = clock

    def execute(self, data: tuple[int, int, str]) -> Booking:
        booking_id, business_id, status = data
        booking = self._bookings.get_by_id(booking_id)
        if booking is None:
            raise BookingNotFound()
        if booking.business_id != business_id:
            raise PermissionDeniedError("Not your business")
        allowed = {
            BOOKING_PENDING: (BOOKING_CONFIRMED, BOOKING_CANCELLED),
            BOOKING_CONFIRMED: (BOOKING_COMPLETED, BOOKING_NO_SHOW, BOOKING_CANCELLED),
        }.get(booking.status, ())
        if status not in allowed:
            raise InvalidBookingStatus(f"Cannot move from {booking.status} to {status}")
        booking.status = status
        return self._bookings.update(booking)
