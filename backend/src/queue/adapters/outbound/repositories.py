"""Persistence adapters: ORM <-> entity mappings for the queue feature."""

from __future__ import annotations

from src.queue.adapters.outbound.orm_models import QueueEntryModel, ServiceModel
from src.queue.domain.entities import QueueEntry, Service
from src.queue.domain.ports import (
    BusinessReader,
    QueueEntryRepository,
    ServiceReader,
    ServiceRepository,
)


# --------------------------------------------------------------------------- #
# Service
# --------------------------------------------------------------------------- #
class DjangoServiceRepository(ServiceRepository):
    def get_by_id(self, service_id: int) -> Service | None:
        row = ServiceModel.objects.filter(pk=service_id).first()
        return self._to_entity(row) if row else None

    def list_by_business(self, business_id: int, active_only: bool = True) -> list[Service]:
        qs = ServiceModel.objects.filter(business_id=business_id)
        if active_only:
            qs = qs.filter(is_active=True)
        return [self._to_entity(r) for r in qs.order_by("display_order", "id")]

    def list_active_by_business(self, business_id: int) -> list[Service]:
        return self.list_by_business(business_id, active_only=True)

    def add(self, *, business_id, name, ticket_prefix, description,
            avg_duration_sec, display_order) -> Service:
        row = ServiceModel.objects.create(
            business_id=business_id,
            name=name,
            ticket_prefix=ticket_prefix,
            description=description,
            avg_duration_sec=avg_duration_sec,
            display_order=display_order,
        )
        return self._to_entity(row)

    def update(self, service: Service) -> Service:
        ServiceModel.objects.filter(pk=service.id).update(
            name=service.name,
            description=service.description,
            ticket_prefix=service.ticket_prefix,
            avg_duration_sec=service.avg_duration_sec,
            is_active=service.is_active,
            display_order=service.display_order,
        )
        return self._to_entity(ServiceModel.objects.get(pk=service.id))

    def exists_prefix(self, business_id: int, prefix: str) -> bool:
        return ServiceModel.objects.filter(business_id=business_id, ticket_prefix=prefix).exists()

    def next_display_order(self, business_id: int) -> int:
        last = (
            ServiceModel.objects.filter(business_id=business_id)
            .order_by("-display_order")
            .first()
        )
        return (last.display_order + 1) if last else 0

    def has_active_entries(self, service_id: int) -> bool:
        return QueueEntryModel.objects.filter(
            service_id=service_id, status__in=("waiting", "called", "in_progress")
        ).exists()

    @staticmethod
    def _to_entity(row: ServiceModel) -> Service:
        return Service(
            id=row.pk,
            business_id=row.business_id,
            name=row.name,
            ticket_prefix=row.ticket_prefix,
            description=row.description,
            avg_duration_sec=row.avg_duration_sec,
            is_active=row.is_active,
            display_order=row.display_order,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


# --------------------------------------------------------------------------- #
# Queue entries
# --------------------------------------------------------------------------- #
class DjangoQueueEntryRepository(QueueEntryRepository):
    def get_by_id(self, entry_id: int) -> QueueEntry | None:
        row = QueueEntryModel.objects.filter(pk=entry_id).first()
        return self._to_entity(row) if row else None

    def add(self, *, business_id, service_id, ticket_number, ticket_code,
            user_id, display_name, ticket_date) -> QueueEntry:
        row = QueueEntryModel.objects.create(
            business_id=business_id,
            service_id=service_id,
            ticket_number=ticket_number,
            ticket_code=ticket_code,
            user_id=user_id,
            display_name=display_name or "",
            ticket_date=ticket_date,
        )
        return self._to_entity(row)

    def list_active_by_service(self, service_id: int) -> list[QueueEntry]:
        rows = QueueEntryModel.objects.filter(
            service_id=service_id, status__in=("waiting", "called", "in_progress")
        ).order_by("created_at")
        return [self._to_entity(r) for r in rows]

    def list_active_by_business(self, business_id: int) -> list[QueueEntry]:
        rows = QueueEntryModel.objects.filter(
            business_id=business_id, status__in=("waiting", "called", "in_progress")
        ).order_by("created_at")
        return [self._to_entity(r) for r in rows]

    def list_by_user(self, user_id: int) -> list[QueueEntry]:
        rows = QueueEntryModel.objects.filter(user_id=user_id).order_by("-created_at")
        return [self._to_entity(r) for r in rows]

    def active_for_user_and_service(self, user_id: int, service_id: int) -> QueueEntry | None:
        row = QueueEntryModel.objects.filter(
            user_id=user_id,
            service_id=service_id,
            status__in=("waiting", "called", "in_progress"),
        ).first()
        return self._to_entity(row) if row else None

    def last_ticket_for_service_on_day(
        self, service_id: int, ticket_date: str
    ) -> QueueEntry | None:
        row = (
            QueueEntryModel.objects.filter(service_id=service_id, ticket_date=ticket_date)
            .order_by("-ticket_number")
            .first()
        )
        return self._to_entity(row) if row else None

    def update(self, entry: QueueEntry) -> QueueEntry:
        QueueEntryModel.objects.filter(pk=entry.id).update(
            status=entry.status,
            display_name=entry.display_name or "",
            called_at=entry.called_at,
            started_at=entry.started_at,
            served_at=entry.served_at,
            alert_sent=entry.alert_sent,
        )
        return self._to_entity(QueueEntryModel.objects.get(pk=entry.id))

    @staticmethod
    def _to_entity(row: QueueEntryModel) -> QueueEntry:
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


# --------------------------------------------------------------------------- #
# Read-only adapters used cross-feature (satisfy ServiceReader / BusinessReader)
# --------------------------------------------------------------------------- #
class DjangoServiceReader(ServiceReader):
    """Thin read-only view of services for other features (e.g. bookings)."""

    def get_by_id(self, service_id: int) -> Service | None:
        return DjangoServiceRepository().get_by_id(service_id)

    def list_active_by_business(self, business_id: int) -> list[Service]:
        return DjangoServiceRepository().list_by_business(business_id, active_only=True)


class DjangoBusinessReader(BusinessReader):
    def get_timezone(self, business_id: int) -> str:
        from src.businesses.adapters.outbound.orm_models import BusinessModel

        row = BusinessModel.objects.filter(pk=business_id).only("timezone").first()
        return row.timezone if row else "UTC"
