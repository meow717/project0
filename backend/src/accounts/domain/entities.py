"""Accounts domain entities and value objects (pure Python)."""

from __future__ import annotations

from dataclasses import dataclass

from src.shared.domain.entity import Entity


@dataclass(kw_only=True)
class User(Entity):
    email: str
    full_name: str = ""
    is_active: bool = True
    is_staff: bool = False
    # Opaque hash produced by the PasswordHasher port; never the raw password.
    password_hash: str | None = None


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"
