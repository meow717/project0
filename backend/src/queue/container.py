"""Composition root for the queue feature (wires adapters to use cases)."""

from __future__ import annotations

from functools import lru_cache

from django.conf import settings

from src.queue.adapters.outbound.alerts import NotificationsGatewayAdapter
from src.queue.adapters.outbound.live_view import DjangoLiveQueueView, DjangoStatsView
from src.queue.adapters.outbound.repositories import (
    DjangoBusinessReader,
    DjangoQueueEntryRepository,
    DjangoServiceRepository,
)
from src.queue.application.use_cases import (
    CallNext,
    CancelEntry,
    CompleteServing,
    CreateService,
    CreateWalkInEntry,
    DeactivateService,
    GetBusinessEntries,
    GetEntry,
    GetLiveSnapshot,
    GetMyEntries,
    GetService,
    GetStats,
    GetWaitEstimate,
    JoinQueue,
    ListServices,
    MarkNoShow,
    StartServing,
    UpdateService,
)
from src.shared.domain.ports import CachePort, Clock, SystemClock
from src.shared.infrastructure.cache import DjangoCacheAdapter


class QueueContainer:
    def __init__(self) -> None:
        self.services = DjangoServiceRepository()
        self.entries = DjangoQueueEntryRepository()
        self.businesses = DjangoBusinessReader()
        self.clock: Clock = SystemClock()
        self.cache: CachePort = DjangoCacheAdapter()
        self.notifications = NotificationsGatewayAdapter()
        self.live_view = DjangoLiveQueueView(self.clock)
        self.stats_view = DjangoStatsView()

        # Alert lead time (seconds) — how far in advance to notify.
        self.alert_lead_sec = getattr(settings, "ALERT_LEAD_SECONDS", 900)
        self.live_ttl = getattr(settings, "LIVE_SNAPSHOT_TTL_SECONDS", 5)

    @property
    def create_service(self) -> CreateService:
        return CreateService(self.services)

    @property
    def list_services(self) -> ListServices:
        return ListServices(self.services)

    @property
    def get_service(self) -> GetService:
        return GetService(self.services)

    @property
    def update_service(self) -> UpdateService:
        return UpdateService(self.services)

    @property
    def deactivate_service(self) -> DeactivateService:
        return DeactivateService(self.services)

    @property
    def join_queue(self) -> JoinQueue:
        return JoinQueue(self.services, self.entries, self.clock, self.businesses)

    @property
    def create_walk_in(self) -> CreateWalkInEntry:
        return CreateWalkInEntry(self.services, self.entries, self.clock, self.businesses)

    @property
    def call_next(self) -> CallNext:
        return CallNext(
            self.entries, self.services, self.cache, self.clock,
            self.notifications, self.alert_lead_sec,
        )

    @property
    def start_serving(self) -> StartServing:
        return StartServing(self.entries, self.cache, self.clock)

    @property
    def complete_serving(self) -> CompleteServing:
        return CompleteServing(self.entries, self.services, self.cache, self.clock)

    @property
    def mark_no_show(self) -> MarkNoShow:
        return MarkNoShow(self.entries, self.cache, self.clock)

    @property
    def cancel_entry(self) -> CancelEntry:
        return CancelEntry(self.entries, self.cache, self.clock)

    @property
    def get_my_entries(self) -> GetMyEntries:
        return GetMyEntries(self.entries)

    @property
    def list_business_entries(self) -> GetBusinessEntries:
        return GetBusinessEntries(self.entries)

    @property
    def get_entry(self) -> GetEntry:
        return GetEntry(self.entries)

    @property
    def get_wait_estimate(self) -> GetWaitEstimate:
        return GetWaitEstimate(self.entries, self.services)

    @property
    def get_live_snapshot(self) -> GetLiveSnapshot:
        return GetLiveSnapshot(self.cache, self.live_view)

    @property
    def get_stats(self) -> GetStats:
        return GetStats(self.stats_view)


@lru_cache(maxsize=1)
def container() -> QueueContainer:
    return QueueContainer()
