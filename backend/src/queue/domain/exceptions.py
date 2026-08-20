"""Queue domain exceptions (subclass the shared hierarchy)."""

from __future__ import annotations

from src.shared.domain.exceptions import ConflictError, NotFoundError, ValidationError


class ServiceNotFound(NotFoundError):
    code = "service_not_found"


class EntryNotFound(NotFoundError):
    code = "entry_not_found"


class ServiceInactive(ValidationError):
    code = "service_inactive"


class AlreadyInQueue(ConflictError):
    code = "already_in_queue"


class InvalidTransition(ConflictError):
    code = "invalid_transition"


class QueueClosed(ConflictError):
    code = "queue_closed"
