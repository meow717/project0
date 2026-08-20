"""Application use cases for the queue feature.

Every operation is a single use case: parse the command, orchestrate the domain
through the injected ports, raise domain exceptions on failure. No Django or
HTTP here — only business rules.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from src.queue.domain.entities import (
    ACTIVE_STATUSES,
    STATUS_CALLED,
    STATUS_CANCELLED,
    STATUS_IN_PROGRESS,
    STATUS_NO_SHOW,
    STATUS_SERVED,
    STATUS_WAITING,
    QueueEntry,
    QueueSnapshot,
    Service,
    ServiceLiveStatus,
    StatsReport,
    TicketCode,
    WaitEstimate,
)
from src.queue.domain.exceptions import (
    AlreadyInQueue,
    EntryNotFound,
    InvalidTransition,
    QueueClosed,
    ServiceInactive,
    ServiceNotFound,
)
from src.queue.domain.ports import (
    BusinessReader,
    Clock,
    LiveQueueView,
    NotificationGateway,
    QueueEntryRepository,
    ServiceRepository,
    StatsView,
)
from src.queue.domain.wait_estimator import estimate_wait, position_of, update_avg_duration
from src.shared.application.use_case import UseCase
from src.shared.domain.exceptions import PermissionDeniedError, ValidationError
from src.shared.domain.ports import CachePort
from src.shared.domain.timezones import local_day


# --------------------------------------------------------------------------- #
# Service management
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class CreateServiceCommand:
    business_id: int
    name: str
    ticket_prefix: str
    description: str = ""
    avg_duration_sec: int = 600


@dataclass(frozen=True)
class UpdateServiceCommand:
    service_id: int
    name: str | None = None
    description: str | None = None
    avg_duration_sec: int | None = None


class CreateService(UseCase[CreateServiceCommand, Service]):
    def __init__(self, services: ServiceRepository) -> None:
        self._services = services

    def execute(self, data: CreateServiceCommand) -> Service:
        prefix = data.ticket_prefix.strip().upper()
        if not prefix or len(prefix) > 2:
            raise ValidationError("Ticket prefix must be 1-2 characters")
        if self._services.exists_prefix(data.business_id, prefix):
            raise AlreadyInQueue("Ticket prefix already in use")
        return self._services.add(
            business_id=data.business_id,
            name=data.name.strip(),
            ticket_prefix=prefix,
            description=data.description.strip(),
            avg_duration_sec=max(1, data.avg_duration_sec),
            display_order=self._services.next_display_order(data.business_id),
        )


class GetService(UseCase[int, Service]):
    def __init__(self, services: ServiceRepository) -> None:
        self._services = services

    def execute(self, service_id: int) -> Service:
        service = self._services.get_by_id(service_id)
        if service is None:
            raise ServiceNotFound()
        return service


class ListServices(UseCase[int, list[Service]]):
    def __init__(self, services: ServiceRepository) -> None:
        self._services = services

    def execute(self, business_id: int) -> list[Service]:
        return self._services.list_by_business(business_id, active_only=False)


class UpdateService(UseCase[UpdateServiceCommand, Service]):
    def __init__(self, services: ServiceRepository) -> None:
        self._services = services

    def execute(self, data: UpdateServiceCommand) -> Service:
        service = self._services.get_by_id(data.service_id)
        if service is None:
            raise ServiceNotFound()
        if data.name is not None:
            service.name = data.name.strip()
        if data.description is not None:
            service.description = data.description.strip()
        if data.avg_duration_sec is not None:
            service.avg_duration_sec = max(1, data.avg_duration_sec)
        return self._services.update(service)


class DeactivateService(UseCase[int, Service]):
    def __init__(self, services: ServiceRepository) -> None:
        self._services = services

    def execute(self, service_id: int) -> Service:
        service = self._services.get_by_id(service_id)
        if service is None:
            raise ServiceNotFound()
        if self._services.has_active_entries(service_id):
            raise InvalidTransition("Cannot deactivate a service with active entries")
        service.is_active = False
        return self._services.update(service)


# --------------------------------------------------------------------------- #
# Joining / walk-ins
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class JoinQueueCommand:
    service_id: int
    user_id: int
    display_name: str | None = None


class JoinQueue(UseCase[JoinQueueCommand, QueueEntry]):
    def __init__(
        self,
        services: ServiceRepository,
        entries: QueueEntryRepository,
        clock: Clock,
        businesses: BusinessReader,
    ) -> None:
        self._services = services
        self._entries = entries
        self._clock = clock
        self._businesses = businesses

    def execute(self, data: JoinQueueCommand) -> QueueEntry:
        service = self._services.get_by_id(data.service_id)
        if service is None:
            raise ServiceNotFound()
        if not service.is_active:
            raise ServiceInactive()
        if self._entries.active_for_user_and_service(data.user_id, service.id) is not None:
            raise AlreadyInQueue("You already have an active ticket in this queue")

        now = self._clock.now()
        ticket_date = self._ticket_date(service.business_id, now)
        last = self._entries.last_ticket_for_service_on_day(service.id, ticket_date)
        number = (last.ticket_number + 1) if last else 1
        return self._entries.add(
            business_id=service.business_id,
            service_id=service.id,
            ticket_number=number,
            ticket_code=str(TicketCode(service.ticket_prefix, number)),
            user_id=data.user_id,
            display_name=data.display_name,
            ticket_date=ticket_date,
        )

    def _ticket_date(self, business_id: int, now) -> str:
        return local_day(now, self._businesses.get_timezone(business_id))


class CreateWalkInEntry(UseCase[JoinQueueCommand, QueueEntry]):
    """A staff-created entry with an optional display name (guest)."""

    def __init__(
        self,
        services: ServiceRepository,
        entries: QueueEntryRepository,
        clock: Clock,
        businesses: BusinessReader,
    ) -> None:
        self._services = services
        self._entries = entries
        self._clock = clock
        self._businesses = businesses

    def execute(self, data: JoinQueueCommand) -> QueueEntry:
        service = self._services.get_by_id(data.service_id)
        if service is None:
            raise ServiceNotFound()
        if not service.is_active:
            raise ServiceInactive()

        now = self._clock.now()
        ticket_date = self._ticket_date(service.business_id, now)
        last = self._entries.last_ticket_for_service_on_day(service.id, ticket_date)
        number = (last.ticket_number + 1) if last else 1
        return self._entries.add(
            business_id=service.business_id,
            service_id=service.id,
            ticket_number=number,
            ticket_code=str(TicketCode(service.ticket_prefix, number)),
            user_id=data.user_id,
            display_name=data.display_name,
            ticket_date=ticket_date,
        )

    def _ticket_date(self, business_id: int, now) -> str:
        return local_day(now, self._businesses.get_timezone(business_id))


# --------------------------------------------------------------------------- #
# Staff transitions
# --------------------------------------------------------------------------- #
class _TransitionUseCase(UseCase):
    def __init__(self, entries: QueueEntryRepository, services: ServiceRepository,
                 cache: CachePort, clock: Clock) -> None:
        self._entries = entries
        self._services = services
        self._cache = cache
        self._clock = clock

    def _get_owned(self, entry_id: int, business_id: int) -> QueueEntry:
        entry = self._entries.get_by_id(entry_id)
        if entry is None:
            raise EntryNotFound()
        if entry.business_id != business_id:
            raise PermissionDeniedError("Not your queue")
        return entry

    def _invalidate(self, business_id: int) -> None:
        self._cache.delete(f"sq:live:{business_id}")

    def _transition(self, entry: QueueEntry, to: str, *, field: str) -> QueueEntry:
        if entry.status == STATUS_SERVED or entry.status == to:
            raise InvalidTransition(f"Cannot move from {entry.status} to {to}")
        setattr(entry, field, self._clock.now())
        entry.status = to
        return self._entries.update(entry)


class CallNext(UseCase[tuple[int, int], QueueEntry]):
    """Call the oldest waiting entry of a service. ``business_id`` guards staff."""

    def __init__(self, entries: QueueEntryRepository, services: ServiceRepository,
                 cache: CachePort, clock: Clock,
                 notifications: NotificationGateway, alert_lead_sec: int) -> None:
        self._entries = entries
        self._services = services
        self._cache = cache
        self._clock = clock
        self._notifications = notifications
        self._alert_lead_sec = alert_lead_sec

    def execute(self, data: tuple[int, int]) -> QueueEntry:
        service_id, business_id = data
        service = self._services.get_by_id(service_id)
        if service is None or service.business_id != business_id:
            raise PermissionDeniedError("Not your service")
        active = [e for e in self._entries.list_active_by_service(service_id)
                  if e.status == STATUS_WAITING]
        if not active:
            raise QueueClosed("No one is waiting")
        entry = active[0]
        entry.status = STATUS_CALLED
        entry.called_at = self._clock.now()
        result = self._entries.update(entry)
        self._cache.delete(f"sq:live:{business_id}")

        # After calling, re-check the wait of everyone behind.
        self._maybe_alert_others(service_id, business_id)
        return result

    def _maybe_alert_others(self, service_id: int, business_id: int) -> None:
        from src.queue.domain.wait_estimator import estimate_wait

        active = self._entries.list_active_by_service(service_id)
        services = {s.id: s for s in self._services.list_active_by_business(business_id)}
        wait_total = estimate_wait(active, services)
        # Walk from the front: each waiting entry's remaining wait shrinks by the
        # duration of the entries ahead. Approximate by subtracting sequential avgs.
        running = wait_total
        for e in active:
            service = services.get(e.service_id)
            avg = service.avg_duration_sec if service else 600
            if e.status == STATUS_WAITING and e.user_id:
                running -= avg if running >= avg else running
                if running <= self._alert_lead_sec:
                    if not e.alert_sent:
                        e.alert_sent = True
                        self._entries.update(e)
                        self._notifications.send(
                            user_id=e.user_id,
                            title="Your turn is coming",
                            body=(
                                f"Your ticket {e.ticket_code} is almost up. "
                                "Please head to the venue."
                            ),
                            kind="in_app",
                            ref_kind="queue",
                            ref_id=e.id,
                        )


class StartServing(UseCase[tuple[int, int], QueueEntry]):
    def __init__(self, entries: QueueEntryRepository, cache: CachePort, clock: Clock) -> None:
        self._entries = entries
        self._cache = cache
        self._clock = clock

    def execute(self, data: tuple[int, int]) -> QueueEntry:
        entry_id, business_id = data
        entry = self._entries.get_by_id(entry_id)
        if entry is None:
            raise EntryNotFound()
        if entry.business_id != business_id:
            raise PermissionDeniedError("Not your queue")
        if entry.status != STATUS_CALLED:
            raise InvalidTransition("Only a called entry can start")
        entry.status = STATUS_IN_PROGRESS
        entry.started_at = self._clock.now()
        result = self._entries.update(entry)
        self._cache.delete(f"sq:live:{business_id}")
        return result


class CompleteServing(UseCase[tuple[int, int], QueueEntry]):
    def __init__(self, entries: QueueEntryRepository, services: ServiceRepository,
                 cache: CachePort, clock: Clock) -> None:
        self._entries = entries
        self._services = services
        self._cache = cache
        self._clock = clock

    def execute(self, data: tuple[int, int]) -> QueueEntry:
        entry_id, business_id = data
        entry = self._entries.get_by_id(entry_id)
        if entry is None:
            raise EntryNotFound()
        if entry.business_id != business_id:
            raise PermissionDeniedError("Not your queue")
        if entry.status != STATUS_IN_PROGRESS:
            raise InvalidTransition("Only an in-progress entry can be completed")
        entry.status = STATUS_SERVED
        entry.served_at = self._clock.now()
        result = self._entries.update(entry)

        # EMA update on the service.
        service = self._services.get_by_id(entry.service_id)
        if service and entry.started_at:
            duration = (entry.served_at - entry.started_at).total_seconds()
            service.avg_duration_sec = update_avg_duration(service.avg_duration_sec, int(duration))
            self._services.update(service)

        self._cache.delete(f"sq:live:{business_id}")
        return result


class MarkNoShow(UseCase[tuple[int, int], QueueEntry]):
    def __init__(self, entries: QueueEntryRepository, cache: CachePort, clock: Clock) -> None:
        self._entries = entries
        self._cache = cache
        self._clock = clock

    def execute(self, data: tuple[int, int]) -> QueueEntry:
        entry_id, business_id = data
        entry = self._entries.get_by_id(entry_id)
        if entry is None:
            raise EntryNotFound()
        if entry.business_id != business_id:
            raise PermissionDeniedError("Not your queue")
        if entry.status not in (STATUS_WAITING, STATUS_CALLED):
            raise InvalidTransition("Only waiting or called entries can be marked no-show")
        entry.status = STATUS_NO_SHOW
        result = self._entries.update(entry)
        self._cache.delete(f"sq:live:{business_id}")
        return result


class CancelEntry(UseCase[tuple[int, int], QueueEntry]):
    """Customer cancels their own waiting ticket."""

    def __init__(self, entries: QueueEntryRepository, cache: CachePort, clock: Clock) -> None:
        self._entries = entries
        self._cache = cache
        self._clock = clock

    def execute(self, data: tuple[int, int]) -> QueueEntry:
        entry_id, user_id = data
        entry = self._entries.get_by_id(entry_id)
        if entry is None or entry.user_id != user_id:
            raise EntryNotFound()
        if entry.status != STATUS_WAITING:
            raise InvalidTransition("Only waiting entries can be cancelled")
        entry.status = STATUS_CANCELLED
        result = self._entries.update(entry)
        self._cache.delete(f"sq:live:{entry.business_id}")
        return result


# --------------------------------------------------------------------------- #
# Customer reads
# --------------------------------------------------------------------------- #
class GetMyEntries(UseCase[int, list[QueueEntry]]):
    def __init__(self, entries: QueueEntryRepository) -> None:
        self._entries = entries

    def execute(self, user_id: int) -> list[QueueEntry]:
        return self._entries.list_by_user(user_id)


class GetBusinessEntries(UseCase[int, list[QueueEntry]]):
    """All active entries of a business, for the staff board."""

    def __init__(self, entries: QueueEntryRepository) -> None:
        self._entries = entries

    def execute(self, business_id: int) -> list[QueueEntry]:
        return self._entries.list_active_by_business(business_id)


class GetEntry(UseCase[tuple[int, int, str], QueueEntry]):
    """Entry detail with ownership check (customer sees own; staff sees own business)."""

    def __init__(self, entries: QueueEntryRepository) -> None:
        self._entries = entries

    def execute(self, data: tuple[int, int, str]) -> QueueEntry:
        entry_id, requester_id, role = data
        entry = self._entries.get_by_id(entry_id)
        if entry is None:
            raise EntryNotFound()
        if role != "staff" and entry.user_id != requester_id:
            raise PermissionDeniedError("Not your ticket")
        return entry


class GetWaitEstimate(UseCase[tuple[int, int], WaitEstimate]):
    def __init__(self, entries: QueueEntryRepository, services: ServiceRepository) -> None:
        self._entries = entries
        self._services = services

    def execute(self, data: tuple[int, int]) -> WaitEstimate:
        entry_id, user_id = data
        entry = self._entries.get_by_id(entry_id)
        if entry is None or entry.user_id != user_id:
            raise EntryNotFound()
        if entry.status not in ACTIVE_STATUSES:
            return WaitEstimate(entry_id=entry.id, position=0, est_seconds=0)

        active = self._entries.list_active_by_service(entry.service_id)
        services = {s.id: s for s in self._services.list_active_by_business(entry.business_id)}
        pos = position_of(entry, active)
        wait = estimate_wait(active, services)
        return WaitEstimate(entry_id=entry.id, position=pos, est_seconds=wait)


# --------------------------------------------------------------------------- #
# Live snapshot (read model, cache-backed)
# --------------------------------------------------------------------------- #
class GetLiveSnapshot(UseCase[tuple[int, int], QueueSnapshot]):
    """Returns the cached snapshot for a business, recomputing on cache miss.

    ``data`` = (business_id, ttl_seconds).
    """

    def __init__(self, cache: CachePort, view: LiveQueueView) -> None:
        self._cache = cache
        self._view = view

    def execute(self, data: tuple[int, int]) -> QueueSnapshot:
        business_id, ttl = data
        key = f"sq:live:{business_id}"
        cached = self._cache.get(key)
        if cached is not None:
            try:
                return self._snapshot_from_json(business_id, cached)
            except ValueError:
                pass  # corrupt cache -> recompute
        snapshot = self._view.build(business_id)
        self._cache.set(key, json.dumps(snapshot_to_dict(snapshot)), ttl)
        return snapshot

    @staticmethod
    def _snapshot_from_json(business_id: int, raw: str) -> QueueSnapshot:
        data = json.loads(raw)
        from datetime import datetime

        return QueueSnapshot(
            business_id=business_id,
            generated_at=datetime.fromisoformat(data["generated_at"]),
            crowd_level=data["crowd_level"],
            services=[ServiceLiveStatus(**s) for s in data["services"]],
        )


class GetStats(UseCase[int, StatsReport]):
    """Staff dashboard statistics, computed by the outbound stats view."""

    def __init__(self, view: StatsView) -> None:
        self._view = view

    def execute(self, business_id: int) -> StatsReport:
        return self._view.build(business_id)


# --------------------------------------------------------------------------- #
# Snapshot serialization helpers (pure functions)
# --------------------------------------------------------------------------- #
def snapshot_to_dict(snapshot: QueueSnapshot) -> dict:
    return {
        "business_id": snapshot.business_id,
        "generated_at": snapshot.generated_at.isoformat(),
        "crowd_level": snapshot.crowd_level,
        "services": [
            {
                "service_id": s.service_id,
                "name": s.name,
                "prefix": s.prefix,
                "current_number": s.current_number,
                "waiting_count": s.waiting_count,
                "est_wait_min": s.est_wait_min,
                "state": s.state,
            }
            for s in snapshot.services
        ],
    }
