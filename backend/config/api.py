"""
Composition of the HTTP layer.

A single ``NinjaAPI`` instance mounts every feature's inbound router and maps
domain exceptions to HTTP responses in one place (DRY). Features never import
each other; they only register a router here.
"""

from __future__ import annotations

from django.http import HttpRequest
from ninja import NinjaAPI
from ninja.errors import ValidationError

from src.accounts.adapters.inbound.router import router as accounts_router
from src.bookings.adapters.inbound.router import (
    router as bookings_router,
)
from src.bookings.adapters.inbound.router import (
    staff_router as bookings_staff_router,
)
from src.businesses.adapters.inbound.router import (
    router as businesses_router,
)
from src.businesses.adapters.inbound.router import (
    staff_router as businesses_staff_router,
)
from src.notifications.adapters.inbound.router import router as notifications_router
from src.queue.adapters.inbound.router import (
    queue_router,
)
from src.queue.adapters.inbound.router import (
    router as services_router,
)
from src.queue.adapters.inbound.router import (
    staff_router as queue_staff_router,
)
from src.shared.domain.exceptions import (
    AuthenticationError,
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDeniedError,
)
from src.shared.domain.exceptions import (
    ValidationError as DomainValidationError,
)

api = NinjaAPI(title="Karkh API", version="1.0.0", description="Hexagonal Django + Ninja backend")

# --------------------------------------------------------------------------- #
# Health check (used by Render / uptime monitors)
# --------------------------------------------------------------------------- #
@api.get("/health", response=dict, auth=None)
def health(request):
    return {"status": "ok"}


# --------------------------------------------------------------------------- #
# Feature routers
# --------------------------------------------------------------------------- #
api.add_router("/auth", accounts_router, tags=["auth"])
api.add_router("/businesses", businesses_router, tags=["businesses"])
api.add_router("/services", services_router, tags=["services"])
api.add_router("/queue", queue_router, tags=["queue"])
api.add_router("/staff", businesses_staff_router, tags=["staff"])
api.add_router("/staff", queue_staff_router, tags=["staff"])
api.add_router("/staff", bookings_staff_router, tags=["staff"])
api.add_router("/bookings", bookings_router, tags=["bookings"])
api.add_router("/notifications", notifications_router, tags=["notifications"])


# --------------------------------------------------------------------------- #
# Domain-exception -> HTTP mapping (single source of truth)
# --------------------------------------------------------------------------- #
_STATUS_BY_EXCEPTION: list[tuple[type[DomainError], int]] = [
    (DomainValidationError, 422),
    (AuthenticationError, 401),
    (PermissionDeniedError, 403),
    (NotFoundError, 404),
    (ConflictError, 409),
]


@api.exception_handler(DomainError)
def handle_domain_error(request: HttpRequest, exc: DomainError):
    status = next((s for kind, s in _STATUS_BY_EXCEPTION if isinstance(exc, kind)), 400)
    return api.create_response(request, {"detail": str(exc), "code": exc.code}, status=status)


@api.exception_handler(ValidationError)
def handle_request_validation(request: HttpRequest, exc: ValidationError):
    return api.create_response(request, {"detail": exc.errors}, status=422)
