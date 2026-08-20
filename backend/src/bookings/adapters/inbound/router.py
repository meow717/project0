"""Inbound HTTP adapter: django-ninja routers for the bookings feature.

Customer router under /api/bookings, staff router under /api/staff. Both thin:
parse -> use case -> serialize.
"""

from __future__ import annotations

from ninja import Router, Status

from src.bookings.adapters.inbound import schemas as s
from src.bookings.application.use_cases import CreateBookingCommand
from src.bookings.container import container
from src.queue.adapters.outbound.repositories import DjangoServiceRepository
from src.shared.infrastructure.auth import AuthPrincipal, JWTAuth, require_staff

router = Router()
staff_router = Router()
jwt_auth = JWTAuth()


def _booking_to_out(booking) -> s.BookingOut:
    service = DjangoServiceRepository().get_by_id(booking.service_id)
    return s.BookingOut(
        id=booking.id,
        business_id=booking.business_id,
        service_id=booking.service_id,
        service_name=service.name if service else "",
        scheduled_at=booking.scheduled_at,
        duration_sec=booking.duration_sec,
        status=booking.status,
        notes=booking.notes,
    )


# --------------------------------------------------------------------------- #
# /api/bookings (customer)
# --------------------------------------------------------------------------- #
@router.post("", response={201: s.BookingOut}, auth=jwt_auth)
def create_booking(request, payload: s.BookingCreateIn):
    principal: AuthPrincipal = request.auth
    booking = container().create_booking.execute(
        CreateBookingCommand(**payload.model_dump(), user_id=principal.id)
    )
    return Status(201, _booking_to_out(booking))


@router.get("/mine", response=list[s.BookingOut], auth=jwt_auth)
def my_bookings(request):
    principal: AuthPrincipal = request.auth
    return [_booking_to_out(b) for b in container().list_my_bookings.execute(principal.id)]


@router.delete("/{booking_id}", response={204: None}, auth=jwt_auth)
def cancel_booking(request, booking_id: int):
    principal: AuthPrincipal = request.auth
    container().cancel_booking.execute((booking_id, principal.id))
    return Status(204, None)


# --------------------------------------------------------------------------- #
# /api/staff/bookings (staff)
# --------------------------------------------------------------------------- #
@staff_router.get("/bookings", response=list[s.BookingOut], auth=jwt_auth)
def business_bookings(request, date: str | None = None):
    principal: AuthPrincipal = require_staff(request.auth)
    business_id = _effective_business(principal)
    day = date or _today_iso(business_id)
    return [
        _booking_to_out(b)
        for b in container().list_business_bookings.execute((business_id, day))
    ]


@staff_router.patch("/bookings/{booking_id}", response=s.BookingOut, auth=jwt_auth)
def set_status(request, booking_id: int, payload: s.BookingStatusIn):
    principal: AuthPrincipal = require_staff(request.auth)
    booking = container().set_booking_status.execute(
        (booking_id, _effective_business(principal), payload.status)
    )
    return _booking_to_out(booking)


def _effective_business(principal: AuthPrincipal) -> int:
    if principal.business_id:
        return principal.business_id
    from src.accounts.models import UserModel

    row = UserModel.objects.filter(pk=principal.id).only("business_id").first()
    if row is None or row.business_id is None:
        from src.shared.domain.exceptions import PermissionDeniedError

        raise PermissionDeniedError("No business linked to your account")
    return row.business_id


def _today_iso(business_id: int) -> str:
    from src.bookings.adapters.outbound.repositories import DjangoBusinessHoursReader

    tz_name, _ = DjangoBusinessHoursReader().get_hours(business_id)
    from datetime import UTC, datetime

    from src.shared.domain.timezones import local_day

    return local_day(datetime.now(UTC), tz_name)
