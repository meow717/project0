"""Read-model adapter: builds the live snapshot for a business from ORM data.

This is the only place that knows how the DB answers "what does the queue look
like right now" — the use case just asks for a snapshot.
"""

from __future__ import annotations

from src.queue.adapters.outbound.orm_models import QueueEntryModel, ServiceModel
from src.queue.domain.entities import (
    STATUS_IN_PROGRESS,
    STATUS_SERVED,
    STATUS_WAITING,
    QueueEntry,
    QueueSnapshot,
    ServedPerDay,
    ServedPerHour,
    Service,
    ServiceLiveStatus,
    ServiceStat,
    StatsReport,
)
from src.queue.domain.ports import LiveQueueView, StatsView
from src.queue.domain.wait_estimator import estimate_wait
from src.shared.domain.ports import Clock, SystemClock


class DjangoLiveQueueView(LiveQueueView):
    """Builds a ``QueueSnapshot`` straight from the database."""

    def __init__(self, clock: Clock | None = None) -> None:
        self._clock: Clock = clock or SystemClock()

    def build(self, business_id: int) -> QueueSnapshot:
        now = self._clock.now()
        services = list(
            ServiceModel.objects.filter(business_id=business_id, is_active=True).order_by(
                "display_order", "id"
            )
        )
        entries = list(
            QueueEntryModel.objects.filter(
                business_id=business_id, status__in=("waiting", "called", "in_progress")
            )
        )

        service_map: dict[int, Service] = {s.pk: _as_service(s) for s in services}
        by_service: dict[int, list[QueueEntry]] = {}
        for row in entries:
            by_service.setdefault(row.service_id, []).append(_as_entry(row))

        statuses = []
        total_waiting = 0
        for service in services:
            es = sorted(by_service.get(service.pk, []), key=lambda e: (e.created_at or now))
            waiting = [e for e in es if e.status == STATUS_WAITING]
            in_progress = [e for e in es if e.status == STATUS_IN_PROGRESS]

            current = None
            if in_progress:
                current = in_progress[0].ticket_code
            elif es:
                current = es[0].ticket_code  # next up / called
            else:
                last = (
                    QueueEntryModel.objects.filter(service_id=service.pk)
                    .order_by("-ticket_number")
                    .first()
                )
                current = last.ticket_code if last else None

            est = estimate_wait(es, service_map, now)
            state = "busy" if in_progress else ("idle" if waiting else "closed")
            total_waiting += len(waiting)
            statuses.append(
                ServiceLiveStatus(
                    service_id=service.pk,
                    name=service.name,
                    prefix=service.ticket_prefix,
                    current_number=current,
                    waiting_count=len(waiting),
                    est_wait_min=max(1, round(est / 60)),
                    state=state,
                )
            )

        crowd = "high" if total_waiting > 20 else ("medium" if total_waiting > 8 else "low")
        return QueueSnapshot(
            business_id=business_id,
            generated_at=now,
            crowd_level=crowd,
            services=statuses,
        )


def _as_service(row: ServiceModel) -> Service:
    return Service(
        id=row.pk,
        business_id=row.business_id,
        name=row.name,
        ticket_prefix=row.ticket_prefix,
        avg_duration_sec=row.avg_duration_sec,
    )


def _as_entry(row: QueueEntryModel) -> QueueEntry:
    return QueueEntry(
        id=row.pk,
        business_id=row.business_id,
        service_id=row.service_id,
        ticket_number=row.ticket_number,
        ticket_code=row.ticket_code,
        status=row.status,
        user_id=row.user_id,
        display_name=row.display_name or None,
        called_at=row.called_at,
        started_at=row.started_at,
        served_at=row.served_at,
        alert_sent=row.alert_sent,
        ticket_date=row.ticket_date,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class DjangoStatsView(StatsView):
    """Aggregates served entries into dashboard stats."""

    def build(self, business_id: int) -> StatsReport:
        served = QueueEntryModel.objects.filter(
            business_id=business_id, status=STATUS_SERVED, served_at__isnull=False
        )

        per_day: dict[str, int] = {}
        per_hour: dict[int, int] = {}
        by_service: dict[int, dict] = {}
        for row in served.only("served_at", "service_id", "started_at"):
            day = row.served_at.date().isoformat()
            per_day[day] = per_day.get(day, 0) + 1
            per_hour[row.served_at.hour] = per_hour.get(row.served_at.hour, 0) + 1
            agg = by_service.setdefault(row.service_id, {"served": 0, "wait_total": 0})
            agg["served"] += 1
            if row.started_at:
                agg["wait_total"] += int((row.served_at - row.started_at).total_seconds())

        names = {
            s.pk: s.name
            for s in ServiceModel.objects.filter(business_id=business_id)
        }
        return StatsReport(
            served_per_day=[
                ServedPerDay(date=day, count=count)
                for day, count in sorted(per_day.items())
            ],
            served_per_hour=[
                ServedPerHour(hour=hour, count=count)
                for hour, count in sorted(per_hour.items())
            ],
            by_service=[
                ServiceStat(
                    service_id=service_id,
                    name=names.get(service_id, f"#{service_id}"),
                    served=agg["served"],
                    avg_wait_min=(
                        round(agg["wait_total"] / agg["served"] / 60) if agg["served"] else 0
                    ),
                )
                for service_id, agg in sorted(by_service.items())
            ],
        )
