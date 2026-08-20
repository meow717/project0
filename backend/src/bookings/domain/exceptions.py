"""Booking domain exceptions."""

from __future__ import annotations

from src.shared.domain.exceptions import ConflictError, NotFoundError, ValidationError


class BookingNotFound(NotFoundError):
    code = "booking_not_found"


class BookingConflict(ConflictError):
    code = "booking_conflict"


class InvalidBookingStatus(ValidationError):
    code = "invalid_booking_status"


class OutsideWorkingHours(ValidationError):
    code = "outside_working_hours"
