"""
Reusable JWT route protection (inbound infrastructure).

``JWTAuth`` is a django-ninja ``HttpBearer`` that any feature can attach to a
route via ``auth=JWTAuth()``. It is stateless: it verifies the access token and
exposes a lightweight ``AuthPrincipal`` as ``request.auth``. Routes that need
the full user load it through their own use case using ``principal.id``.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.http import HttpRequest
from ninja.security import HttpBearer

from src.accounts.domain.entities import ROLE_CUSTOMER
from src.shared.domain.exceptions import (
    AuthenticationError,
    PermissionDeniedError,
)
from src.shared.infrastructure.jwt import JwtCodec


@dataclass(frozen=True)
class AuthPrincipal:
    id: int
    email: str
    role: str = ROLE_CUSTOMER
    business_id: int | None = None


class JWTAuth(HttpBearer):
    def __init__(self) -> None:
        super().__init__()
        self._codec = JwtCodec()

    def authenticate(self, request: HttpRequest, token: str) -> AuthPrincipal | None:
        try:
            payload = self._codec.decode(token, expected_type="access")
        except AuthenticationError:
            return None  # -> ninja responds 401
        return AuthPrincipal(
            id=int(payload["sub"]),
            email=payload.get("email", ""),
            role=payload.get("role", ROLE_CUSTOMER),
            business_id=payload.get("business_id"),
        )


def require_staff(principal: AuthPrincipal) -> AuthPrincipal:
    """Raise 403 unless the caller is staff (or admin) of some business."""
    if principal.role not in ("staff", "admin"):
        raise PermissionDeniedError("Staff access required")
    return principal
