"""Composition root for the bookings feature."""

from __future__ import annotations

from functools import lru_cache

from src.bookings.adapters.outbound.repositories import (
    DjangoBookingRepository,
    DjangoBusinessHoursReader,
)
from src.bookings.application.use_cases import (
    CancelBooking,
    CreateBooking,
    ListBusinessBookings,
    ListMyBookings,
    SetBookingStatus,
)
from src.queue.adapters.outbound.repositories import DjangoServiceReader
from src.shared.domain.ports import Clock, SystemClock


class BookingsContainer:
    def __init__(self) -> None:
        self.bookings = DjangoBookingRepository()
        self.services = DjangoServiceReader()
        self.businesses = DjangoBusinessHoursReader()
        self.clock: Clock = SystemClock()

    @property
    def create_booking(self) -> CreateBooking:
        return CreateBooking(self.bookings, self.services, self.businesses, self.clock)

    @property
    def list_my_bookings(self) -> ListMyBookings:
        return ListMyBookings(self.bookings)

    @property
    def cancel_booking(self) -> CancelBooking:
        return CancelBooking(self.bookings, self.clock)

    @property
    def list_business_bookings(self) -> ListBusinessBookings:
        return ListBusinessBookings(self.bookings)

    @property
    def set_booking_status(self) -> SetBookingStatus:
        return SetBookingStatus(self.bookings, self.clock)


@lru_cache(maxsize=1)
def container() -> BookingsContainer:
    return BookingsContainer()
