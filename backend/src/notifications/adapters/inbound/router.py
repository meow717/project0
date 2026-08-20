"""Inbound HTTP adapter: django-ninja router for the notifications feature."""

from __future__ import annotations

from ninja import Router, Status

from src.notifications.adapters.inbound import schemas as s
from src.notifications.container import container
from src.shared.infrastructure.auth import AuthPrincipal, JWTAuth

router = Router()
jwt_auth = JWTAuth()


@router.get("/mine", response=list[s.NotificationOut], auth=jwt_auth)
def my_notifications(request):
    principal: AuthPrincipal = request.auth
    return container().list_my_notifications.execute(principal.id)


@router.get("/unread", response=s.UnreadOut, auth=jwt_auth)
def unread(request):
    principal: AuthPrincipal = request.auth
    return {"unread_count": container().unread_count.execute(principal.id)}


@router.patch("/{notification_id}/read", response={204: None}, auth=jwt_auth)
def mark_read(request, notification_id: int):
    principal: AuthPrincipal = request.auth
    container().mark_read.execute((notification_id, principal.id))
    return Status(204, None)


@router.post("/read-all", response={204: None}, auth=jwt_auth)
def mark_all_read(request):
    principal: AuthPrincipal = request.auth
    container().mark_all_read.execute(principal.id)
    return Status(204, None)
