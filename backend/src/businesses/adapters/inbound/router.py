"""Inbound HTTP adapter: django-ninja routers for the businesses feature.

Two routers: a public one (directory browsing) and a staff one (create/update/
upload logo) guarded by ``JWTAuth`` + ``require_staff``. Both stay thin — they
parse input, call a use case, and serialize the result.
"""

from __future__ import annotations

from datetime import time

from ninja import File, Router, Status, UploadedFile

from src.businesses.adapters.inbound import schemas as s
from src.businesses.application.use_cases import (
    CreateBusinessCommand,
    UpdateBusinessCommand,
    UploadLogoCommand,
)
from src.businesses.container import container
from src.shared.domain.exceptions import PermissionDeniedError
from src.shared.infrastructure.auth import AuthPrincipal, JWTAuth, require_staff

router = Router()
staff_router = Router()
jwt_auth = JWTAuth()

_PAGE_SIZE = 20


def _parse_time(value: str) -> time:
    hour, minute = (int(p) for p in value.split(":"))
    return time(hour, minute)


def _as_time(value: str | time | None) -> time | None:
    if value is None or isinstance(value, time):
        return value
    return _parse_time(value)


# --------------------------------------------------------------------------- #
# Public directory
# --------------------------------------------------------------------------- #
@router.get("", response=dict, summary="List active businesses")
def list_businesses(request, search: str = "", area: str = "", category: str = "", page: int = 1):
    page = max(page, 1)
    result = container().search_businesses.execute((search, area, category, page, _PAGE_SIZE))
    return {
        "items": result.items,
        "total": result.total,
        "page": result.page,
        "page_size": result.page_size,
    }


@router.get("/{slug}", response=s.BusinessOut)
def get_business(request, slug: str):
    return container().get_business_by_slug.execute(slug)


@router.get("/{slug}/services", response=list[dict])
def business_services(request, slug: str):
    """Active services of a business (public)."""
    business = container().get_business_by_slug.execute(slug)
    from src.queue.adapters.outbound.repositories import DjangoServiceRepository

    services = DjangoServiceRepository().list_by_business(business.id, active_only=True)
    return [
        {
            "id": svc.id,
            "business_id": svc.business_id,
            "name": svc.name,
            "description": svc.description,
            "ticket_prefix": svc.ticket_prefix,
            "avg_duration_sec": svc.avg_duration_sec,
            "is_active": svc.is_active,
        }
        for svc in services
    ]


@router.get("/{slug}/live", response=dict)
def live_snapshot(request, slug: str):
    """Public live snapshot for a business (cache-backed, TTL 5s)."""
    business = container().get_business_by_slug.execute(slug)
    from src.queue.container import container as queue_container

    snapshot = queue_container().get_live_snapshot.execute(
        (business.id, queue_container().live_ttl)
    )
    return {
        "business_id": snapshot.business_id,
        "generated_at": snapshot.generated_at.isoformat(),
        "crowd_level": snapshot.crowd_level,
        "services": [
            {
                "service_id": svc.service_id,
                "name": svc.name,
                "prefix": svc.prefix,
                "current_number": svc.current_number,
                "waiting_count": svc.waiting_count,
                "est_wait_min": svc.est_wait_min,
                "state": svc.state,
            }
            for svc in snapshot.services
        ],
    }


# --------------------------------------------------------------------------- #
# Staff (owns the business)
# --------------------------------------------------------------------------- #
@staff_router.post("/businesses", response={201: s.BusinessOut}, auth=jwt_auth)
def create_business(request, payload: s.BusinessIn):
    """Any authenticated user may create a business; this promotes them to
    staff of it (so the token's role claim is refreshed on next login)."""
    principal: AuthPrincipal = request.auth
    data = payload.model_dump()
    data["opens_at"] = _parse_time(data["opens_at"])
    data["closes_at"] = _parse_time(data["closes_at"])
    return Status(201, container().create_business(
        CreateBusinessCommand(**data, created_by=principal.id)
    ))


@staff_router.put("/businesses/{business_id}", response=s.BusinessOut, auth=jwt_auth)
def update_business(request, business_id: int, payload: s.BusinessUpdateIn):
    principal: AuthPrincipal = require_staff(request.auth)
    _ensure_owns(principal, business_id)
    data = payload.model_dump(exclude_none=True)
    data["opens_at"] = _as_time(data.get("opens_at"))
    data["closes_at"] = _as_time(data.get("closes_at"))
    return container().update_business.execute(
        UpdateBusinessCommand(business_id=business_id, **data)
    )


@staff_router.get("/businesses/me", response=s.BusinessOut, auth=jwt_auth)
def my_business(request):
    """The caller's own business (for the staff dashboard)."""
    principal: AuthPrincipal = require_staff(request.auth)
    business_id = _effective_business(principal)
    return container().get_business.execute(business_id)


@staff_router.patch("/businesses/me", response=s.BusinessOut, auth=jwt_auth)
def update_my_business(request, payload: s.BusinessUpdateIn):
    principal: AuthPrincipal = require_staff(request.auth)
    business_id = _effective_business(principal)
    data = payload.model_dump(exclude_none=True)
    data["opens_at"] = _as_time(data.get("opens_at"))
    data["closes_at"] = _as_time(data.get("closes_at"))
    return container().update_business.execute(
        UpdateBusinessCommand(business_id=business_id, **data)
    )


@staff_router.post("/businesses/{business_id}/logo", response=s.LogoOut, auth=jwt_auth)
def upload_logo(request, business_id: int, file: UploadedFile = File(...)):
    principal: AuthPrincipal = require_staff(request.auth)
    _ensure_owns(principal, business_id)
    content = file.read()
    business = container().upload_business_logo.execute(
        UploadLogoCommand(
            business_id=business_id,
            content=content,
            content_type=file.content_type or "application/octet-stream",
            filename=file.name or "logo",
        )
    )
    return {"logo_url": business.logo_url}


def _ensure_owns(principal: AuthPrincipal, business_id: int) -> None:
    """Staff must own the business. Falls back to the DB so a just-issued
    (pre-business) token still works right after business creation."""
    effective = principal.business_id or _db_business_id(principal.id)
    if effective != business_id:
        raise PermissionDeniedError("Not your business")


def _effective_business(principal: AuthPrincipal) -> int:
    """Resolve the staff user's business id, falling back to the DB."""
    if principal.business_id:
        return principal.business_id
    business_id = _db_business_id(principal.id)
    if business_id is None:
        raise PermissionDeniedError("No business linked to your account")
    return business_id


def _db_business_id(user_id: int) -> int | None:
    from src.accounts.models import UserModel

    row = UserModel.objects.filter(pk=user_id).only("business_id").first()
    return row.business_id if row else None
