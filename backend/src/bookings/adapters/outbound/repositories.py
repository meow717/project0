"""Persistence adapter: maps Booking ORM rows to/from the entity."""

from __future__ import annotations

from datetime import datetime, time

from src.bookings.adapters.outbound.orm_models import BookingModel
from src.bookings.domain.entities import Booking
from src.bookings.domain.ports import BookingRepository
from src.shared.domain.values import BusinessHours


class DjangoBookingRepository(BookingRepository):
    def get_by_id(self, booking_id: int) -> Booking | None:
        row = BookingModel.objects.filter(pk=booking_id).first()
        return self._to_entity(row) if row else None

    def add(self, *, business_id, service_id, user_id, scheduled_at,
            duration_sec, notes) -> Booking:
        row = BookingModel.objects.create(
            business_id=business_id,
            service_id=service_id,
            user_id=user_id,
            scheduled_at=scheduled_at,
            duration_sec=duration_sec,
            notes=notes,
        )
        return self._to_entity(row)

    def list_by_user(self, user_id: int) -> list[Booking]:
        rows = BookingModel.objects.filter(user_id=user_id).order_by("-scheduled_at")
        return [self._to_entity(r) for r in rows]

    def list_by_business_and_date(self, business_id: int, day: str) -> list[Booking]:
        # day is ISO date; bookings on that date (business-local).
        rows = BookingModel.objects.filter(business_id=business_id).order_by("scheduled_at")
        return [self._to_entity(r) for r in rows if r.scheduled_at.date().isoformat() == day]

    def update(self, booking: Booking) -> Booking:
        BookingModel.objects.filter(pk=booking.id).update(
            status=booking.status,
            notes=booking.notes,
            scheduled_at=booking.scheduled_at,
            duration_sec=booking.duration_sec,
        )
        return self._to_entity(BookingModel.objects.get(pk=booking.id))

    def overlapping(self, business_id: int, service_id: int,
                    start: datetime, end: datetime) -> Booking | None:
        row = (
            BookingModel.objects.filter(
                business_id=business_id,
                service_id=service_id,
                scheduled_at__lt=end,
                status__in=("pending", "confirmed"),
            )
            .exclude(scheduled_at__gte=end)
            .first()
        )
        return self._to_entity(row) if row else None

    @staticmethod
    def _to_entity(row: BookingModel) -> Booking:
        return Booking(
            id=row.pk,
            business_id=row.business_id,
            service_id=row.service_id,
            user_id=row.user_id,
            scheduled_at=row.scheduled_at,
            duration_sec=row.duration_sec,
            status=row.status,
            notes=row.notes,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


class DjangoBusinessHoursReader:
    """Satisfies the bookings feature's ``BusinessReader`` port."""

    def get_hours(self, business_id: int) -> tuple[str, BusinessHours]:
        from src.businesses.adapters.outbound.orm_models import BusinessModel

        row = (
            BusinessModel.objects.filter(pk=business_id)
            .only("timezone", "opens_at", "closes_at")
            .first()
        )
        if row is None:
            return "UTC", BusinessHours(opens_at=time(9, 0), closes_at=time(17, 0))
        return row.timezone, BusinessHours(opens_at=row.opens_at, closes_at=row.closes_at)
