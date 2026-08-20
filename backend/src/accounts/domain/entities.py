"""Accounts domain entities and value objects (pure Python)."""

from __future__ import annotations

from dataclasses import dataclass

from src.shared.domain.entity import Entity

ROLE_CUSTOMER = "customer"
ROLE_STAFF = "staff"
ROLE_ADMIN = "admin"
ROLES = (ROLE_CUSTOMER, ROLE_STAFF, ROLE_ADMIN)


@dataclass(kw_only=True)
class User(Entity):
    email: str
    full_name: str = ""
    is_active: bool = True
    is_staff: bool = False
    role: str = ROLE_CUSTOMER
    # Business owned by a ``staff`` user; None for customers/admins.
    business_id: int | None = None
    # Opaque hash produced by the PasswordHasher port; never the raw password.
    password_hash: str | None = None


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"
