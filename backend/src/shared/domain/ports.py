"""
Shared driven ports (framework-agnostic).

These are used by multiple features: time (``Clock``), caching
(``CachePort``) and file storage (``FileStorage``). Each has at least one
infrastructure adapter in ``src/shared/infrastructure``; features depend on the
interfaces here, never on the adapters directly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime


class Clock(ABC):
    """Source of the current instant, so time-based logic is testable."""

    @abstractmethod
    def now(self) -> datetime:
        """Return the current instant (timezone-aware, UTC)."""


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(UTC)


class CachePort(ABC):
    """Small cache abstraction with a per-key TTL (backed by Django cache)."""

    @abstractmethod
    def get(self, key: str) -> str | None: ...

    @abstractmethod
    def set(self, key: str, value: str, ttl_seconds: int) -> None: ...

    @abstractmethod
    def delete(self, key: str) -> None: ...


class FileStorage(ABC):
    """Object storage abstraction (local disk in dev, MinIO/S3 in prod)."""

    @abstractmethod
    def save(self, name: str, content: bytes, content_type: str) -> str:
        """Persist a blob and return its storage key."""

    @abstractmethod
    def url(self, name: str) -> str:
        """Return a (possibly signed) URL for the stored blob."""

    @abstractmethod
    def delete(self, name: str) -> None: ...
