"""Accounts-specific errors, specialising the shared domain errors."""

from __future__ import annotations

from src.shared.domain.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
)


class InvalidCredentials(AuthenticationError):
    code = "invalid_credentials"

    def __init__(self, message: str = "Invalid email or password") -> None:
        super().__init__(message)


class EmailAlreadyUsed(ConflictError):
    code = "email_already_used"

    def __init__(self, message: str = "Email is already registered") -> None:
        super().__init__(message)


class UserNotFound(NotFoundError):
    code = "user_not_found"

    def __init__(self, message: str = "User not found") -> None:
        super().__init__(message)
