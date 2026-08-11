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
# Feature routers
# --------------------------------------------------------------------------- #
api.add_router("/auth", accounts_router, tags=["auth"])


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
