"""
Application use cases for the accounts feature.

Each use case orchestrates the domain and the ports. It contains no Django, no
HTTP and no SQL — only business rules. Dependencies are injected via __init__.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.accounts.domain.entities import TokenPair, User
from src.accounts.domain.exceptions import (
    EmailAlreadyUsed,
    InvalidCredentials,
    UserNotFound,
)
from src.accounts.domain.ports import PasswordHasher, TokenService, UserRepository
from src.shared.application.use_case import UseCase


# --------------------------------------------------------------------------- #
# Commands / results (application DTOs, framework-free)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class RegisterCommand:
    email: str
    password: str
    full_name: str


@dataclass(frozen=True)
class LoginCommand:
    email: str
    password: str


@dataclass(frozen=True)
class AuthResult:
    user: User
    tokens: TokenPair


def _normalize_email(email: str) -> str:
    return email.strip().lower()


# --------------------------------------------------------------------------- #
# Use cases
# --------------------------------------------------------------------------- #
class RegisterUser(UseCase[RegisterCommand, User]):
    def __init__(self, users: UserRepository, hasher: PasswordHasher) -> None:
        self._users = users
        self._hasher = hasher

    def execute(self, data: RegisterCommand) -> User:
        email = _normalize_email(data.email)
        if self._users.exists_by_email(email):
            raise EmailAlreadyUsed()
        password_hash = self._hasher.hash(data.password)
        return self._users.add(
            email=email,
            full_name=data.full_name.strip(),
            password_hash=password_hash,
        )


class AuthenticateUser(UseCase[LoginCommand, AuthResult]):
    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        tokens: TokenService,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens

    def execute(self, data: LoginCommand) -> AuthResult:
        user = self._users.get_by_email(_normalize_email(data.email))
        if (
            user is None
            or not user.is_active
            or not self._hasher.verify(data.password, user.password_hash or "")
        ):
            raise InvalidCredentials()
        return AuthResult(user=user, tokens=self._tokens.issue(user))


class RefreshSession(UseCase[str, TokenPair]):
    def __init__(self, users: UserRepository, tokens: TokenService) -> None:
        self._users = users
        self._tokens = tokens

    def execute(self, refresh_token: str) -> TokenPair:
        user_id = self._tokens.subject_from_refresh(refresh_token)
        user = self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise InvalidCredentials("User is no longer active")
        return self._tokens.issue(user)


class GetCurrentUser(UseCase[int, User]):
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, user_id: int) -> User:
        user = self._users.get_by_id(user_id)
        if user is None:
            raise UserNotFound()
        return user
