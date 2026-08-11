"""
Composition root for the accounts feature.

This is the only place that wires concrete adapters to the ports the use cases
depend on. The router asks the container for a use case; nothing else constructs
adapters. Swap an adapter here (e.g. a different repository) and the whole
feature follows — that is the payoff of Ports & Adapters.
"""

from __future__ import annotations

from functools import lru_cache

from src.accounts.adapters.outbound.hasher import DjangoPasswordHasher
from src.accounts.adapters.outbound.repositories import DjangoUserRepository
from src.accounts.adapters.outbound.tokens import JwtTokenService
from src.accounts.application.use_cases import (
    AuthenticateUser,
    GetCurrentUser,
    RefreshSession,
    RegisterUser,
)


class AccountsContainer:
    def __init__(self) -> None:
        # Adapters are stateless, so a single instance each is fine.
        self.users = DjangoUserRepository()
        self.hasher = DjangoPasswordHasher()
        self.tokens = JwtTokenService()

    @property
    def register_user(self) -> RegisterUser:
        return RegisterUser(self.users, self.hasher)

    @property
    def authenticate_user(self) -> AuthenticateUser:
        return AuthenticateUser(self.users, self.hasher, self.tokens)

    @property
    def refresh_session(self) -> RefreshSession:
        return RefreshSession(self.users, self.tokens)

    @property
    def get_current_user(self) -> GetCurrentUser:
        return GetCurrentUser(self.users)


@lru_cache(maxsize=1)
def container() -> AccountsContainer:
    return AccountsContainer()
