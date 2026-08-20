"""Driven ports for the queue feature."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.queue.domain.entities import QueueEntry, QueueSnapshot, Service, StatsReport


class ServiceRepository(ABC):
    @abstractmethod
    def get_by_id(self, service_id: int) -> Service | None: ...

    @abstractmethod
    def list_by_business(self, business_id: int, active_only: bool = True) -> list[Service]: ...

    @abstractmethod
    def add(self, *, business_id: int, name: str, ticket_prefix: str,
            description: str, avg_duration_sec: int, display_order: int) -> Service: ...

    @abstractmethod
    def update(self, service: Service) -> Service: ...

    @abstractmethod
    def exists_prefix(self, business_id: int, prefix: str) -> bool: ...

    @abstractmethod
    def next_display_order(self, business_id: int) -> int: ...

    @abstractmethod
    def has_active_entries(self, service_id: int) -> bool: ...


class QueueEntryRepository(ABC):
    @abstractmethod
    def get_by_id(self, entry_id: int) -> QueueEntry | None: ...

    @abstractmethod
    def add(self, *, business_id: int, service_id: int, ticket_number: int,
            ticket_code: str, user_id: int | None, display_name: str | None,
            ticket_date: str) -> QueueEntry: ...

    @abstractmethod
    def list_active_by_service(self, service_id: int) -> list[QueueEntry]: ...

    @abstractmethod
    def list_by_user(self, user_id: int) -> list[QueueEntry]: ...

    @abstractmethod
    def active_for_user_and_service(self, user_id: int, service_id: int) -> QueueEntry | None: ...

    @abstractmethod
    def last_ticket_for_service_on_day(
        self, service_id: int, ticket_date: str
    ) -> QueueEntry | None: ...

    @abstractmethod
    def update(self, entry: QueueEntry) -> QueueEntry: ...

    @abstractmethod
    def list_active_by_business(self, business_id: int) -> list[QueueEntry]: ...


class ServiceReader(ABC):
    """Read-only view of services — shared by other features (e.g. bookings)."""

    @abstractmethod
    def get_by_id(self, service_id: int) -> Service | None: ...

    @abstractmethod
    def list_active_by_business(self, business_id: int) -> list[Service]: ...


class BusinessReader(ABC):
    """Read-only view of a business (timezone etc.) for the queue feature."""

    @abstractmethod
    def get_timezone(self, business_id: int) -> str: ...


class NotificationGateway(ABC):
    """Outbound notifications (in-app, email, ...). Implemented by the
    notifications feature through an adapter."""

    @abstractmethod
    def send(self, *, user_id: int, title: str, body: str,
             kind: str, ref_kind: str, ref_id: int) -> None: ...


class LiveQueueView(ABC):
    """Computes the live snapshot (used by the cache-backed read path)."""

    @abstractmethod
    def build(self, business_id: int) -> QueueSnapshot: ...


class StatsView(ABC):
    """Aggregates staff-dashboard statistics for a business."""

    @abstractmethod
    def build(self, business_id: int) -> StatsReport: ...


# --------------------------------------------------------------------------- #
# Clock used inside the queue feature
# --------------------------------------------------------------------------- #
from src.shared.domain.ports import Clock  # noqa: E402  (re-export for clarity)

__all__ = [
    "Clock",
    "ServiceRepository",
    "QueueEntryRepository",
    "ServiceReader",
    "BusinessReader",
    "NotificationGateway",
    "LiveQueueView",
    "StatsView",
]
