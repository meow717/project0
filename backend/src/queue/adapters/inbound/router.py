"""Inbound HTTP adapter: django-ninja routers for the queue feature.

Three logical routers mounted under different prefixes:
  - public services  -> /api/services
  - customer queue   -> /api/queue
  - staff operations -> /api/staff
All stay thin: parse input, call a use case, serialize the result.
"""

from __future__ import annotations

from ninja import Router, Status

from src.queue.adapters.inbound import schemas as s
from src.queue.application.use_cases import (
    CreateServiceCommand,
    JoinQueueCommand,
    UpdateServiceCommand,
)
from src.queue.container import container
from src.shared.infrastructure.auth import AuthPrincipal, JWTAuth, require_staff

router = Router()          # /api/services (public reads + staff writes)
queue_router = Router()    # /api/queue (customer)
staff_router = Router()    # /api/staff (staff)

jwt_auth = JWTAuth()


def _entry_to_out(entry, position=0, est=0) -> s.QueueEntryOut:
    return s.QueueEntryOut(
        id=entry.id,
        business_id=entry.business_id,
        service_id=entry.service_id,
        ticket_code=entry.ticket_code,
        ticket_number=entry.ticket_number,
        status=entry.status,
        position=position,
        est_wait_seconds=est,
        display_name=entry.display_name,
        created_at=entry.created_at,
        called_at=entry.called_at,
        started_at=entry.started_at,
        served_at=entry.served_at,
    )


def _effective_business(principal: AuthPrincipal) -> int:
    """Resolve the staff user's business id, falling back to the DB so a token
    issued before business creation still works."""
    if principal.business_id:
        return principal.business_id
    from src.accounts.models import UserModel

    row = UserModel.objects.filter(pk=principal.id).only("business_id").first()
    if row is None or row.business_id is None:
        from src.shared.domain.exceptions import PermissionDeniedError

        raise PermissionDeniedError("No business linked to your account")
    return row.business_id


# --------------------------------------------------------------------------- #
# /api/services
# --------------------------------------------------------------------------- #
@router.get("/{service_id}", response=s.ServiceOut)
def get_service(request, service_id: int):
    return container().get_service.execute(service_id)


@router.post("", response={201: s.ServiceOut}, auth=jwt_auth)
def create_service(request, payload: s.ServiceCreateIn):
    principal: AuthPrincipal = require_staff(request.auth)
    data = payload.model_dump()
    data["business_id"] = _effective_business(principal)
    return Status(201, container().create_service.execute(CreateServiceCommand(**data)))


@router.patch("/{service_id}", response=s.ServiceOut, auth=jwt_auth)
def update_service(request, service_id: int, payload: s.ServiceUpdateIn):
    principal: AuthPrincipal = require_staff(request.auth)
    service = container().update_service.execute(
        UpdateServiceCommand(service_id=service_id, **payload.model_dump(exclude_none=True))
    )
    if service.business_id != _effective_business(principal):
        from src.shared.domain.exceptions import PermissionDeniedError

        raise PermissionDeniedError("Not your service")
    return service


@router.delete("/{service_id}", response={204: None}, auth=jwt_auth)
def deactivate_service(request, service_id: int):
    principal: AuthPrincipal = require_staff(request.auth)
    service = container().deactivate_service.execute(service_id)
    if service.business_id != _effective_business(principal):
        from src.shared.domain.exceptions import PermissionDeniedError

        raise PermissionDeniedError("Not your service")
    return Status(204, None)


# --------------------------------------------------------------------------- #
# /api/services/{id}/join  (customer)
# --------------------------------------------------------------------------- #
@router.post("/{service_id}/join", response={201: s.QueueEntryOut}, auth=jwt_auth)
def join(request, service_id: int):
    principal: AuthPrincipal = request.auth
    entry = container().join_queue.execute(
        JoinQueueCommand(service_id=service_id, user_id=principal.id)
    )
    return Status(201, _entry_to_out(entry))


# --------------------------------------------------------------------------- #
# /api/queue  (customer)
# --------------------------------------------------------------------------- #
@queue_router.get("/mine", response=list[s.QueueEntryOut], auth=jwt_auth)
def my_entries(request):
    principal: AuthPrincipal = request.auth
    return [_entry_to_out(e) for e in container().get_my_entries.execute(principal.id)]


@queue_router.get("/entries/{entry_id}", response=s.QueueEntryOut, auth=jwt_auth)
def get_entry(request, entry_id: int):
    principal: AuthPrincipal = request.auth
    entry = container().get_entry.execute((entry_id, principal.id, principal.role))
    return _entry_to_out(entry)


@queue_router.get("/entries/{entry_id}/wait", response=s.WaitOut, auth=jwt_auth)
def wait_estimate(request, entry_id: int):
    principal: AuthPrincipal = request.auth
    est = container().get_wait_estimate.execute((entry_id, principal.id))
    return s.WaitOut(position=est.position, est_seconds=est.est_seconds)


@queue_router.delete("/entries/{entry_id}", response={204: None}, auth=jwt_auth)
def cancel_entry(request, entry_id: int):
    principal: AuthPrincipal = request.auth
    container().cancel_entry.execute((entry_id, principal.id))
    return Status(204, None)


# --------------------------------------------------------------------------- #
# /api/staff  (staff only)
# --------------------------------------------------------------------------- #
@staff_router.get("/services", response=list[s.ServiceOut], auth=jwt_auth)
def staff_services(request):
    principal: AuthPrincipal = require_staff(request.auth)
    business_id = _effective_business(principal)
    return container().list_services.execute(business_id)


@staff_router.get("/queue", response=list[s.QueueEntryOut], auth=jwt_auth)
def staff_queue(request):
    """All active entries of the caller's business (board view)."""
    principal: AuthPrincipal = require_staff(request.auth)
    business_id = _effective_business(principal)
    return [_entry_to_out(e) for e in container().list_business_entries.execute(business_id)]


@staff_router.post("/services/{service_id}/call", response=s.QueueEntryOut, auth=jwt_auth)
def call_next(request, service_id: int):
    principal: AuthPrincipal = require_staff(request.auth)
    business_id = _effective_business(principal)
    result = container().call_next.execute((service_id, business_id))
    return _entry_to_out(result)


@staff_router.get("/stats", response=s.StatsReportOut, auth=jwt_auth)
def staff_stats(request):
    principal: AuthPrincipal = require_staff(request.auth)
    business_id = _effective_business(principal)
    return container().get_stats.execute(business_id)


@staff_router.post("/entries", response={201: s.QueueEntryOut}, auth=jwt_auth)
def walk_in(request, payload: s.WalkInIn):
    principal: AuthPrincipal = require_staff(request.auth)
    _effective_business(principal)  # ensures staff has a business
    entry = container().create_walk_in.execute(
        JoinQueueCommand(
            service_id=payload.service_id,
            user_id=None,
            display_name=payload.display_name,
        )
    )
    return Status(201, _entry_to_out(entry))


@staff_router.post("/entries/{entry_id}/call", response=s.QueueEntryOut, auth=jwt_auth)
def call(request, entry_id: int):
    principal: AuthPrincipal = require_staff(request.auth)
    entry = container().get_entry.execute((entry_id, principal.id, "staff"))
    service = container().get_service.execute(entry.service_id)
    result = container().call_next.execute((service.id, _effective_business(principal)))
    return _entry_to_out(result)


@staff_router.post("/entries/{entry_id}/start", response=s.QueueEntryOut, auth=jwt_auth)
def start(request, entry_id: int):
    principal: AuthPrincipal = require_staff(request.auth)
    result = container().start_serving.execute((entry_id, _effective_business(principal)))
    return _entry_to_out(result)


@staff_router.post("/entries/{entry_id}/complete", response=s.QueueEntryOut, auth=jwt_auth)
def complete(request, entry_id: int):
    principal: AuthPrincipal = require_staff(request.auth)
    result = container().complete_serving.execute((entry_id, _effective_business(principal)))
    return _entry_to_out(result)


@staff_router.post("/entries/{entry_id}/no-show", response=s.QueueEntryOut, auth=jwt_auth)
def no_show(request, entry_id: int):
    principal: AuthPrincipal = require_staff(request.auth)
    result = container().mark_no_show.execute((entry_id, _effective_business(principal)))
    return _entry_to_out(result)
