"""
Ports (interfaces) for the accounts feature.

The application layer depends only on these abstractions. Concrete adapters in
``adapters/outbound`` implement them (Django ORM, Argon2, PyJWT).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.accounts.domain.entities import TokenPair, User


class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def exists_by_email(self, email: str) -> bool: ...

    @abstractmethod
    def add(self, *, email: str, full_name: str, password_hash: str) -> User: ...


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, raw_password: str) -> str: ...

    @abstractmethod
    def verify(self, raw_password: str, hashed: str) -> bool: ...


class TokenService(ABC):
    @abstractmethod
    def issue(self, user: User) -> TokenPair: ...

    @abstractmethod
    def subject_from_refresh(self, refresh_token: str) -> int: ...
