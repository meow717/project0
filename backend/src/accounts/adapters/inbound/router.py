"""Inbound HTTP adapter: the django-ninja router for the accounts feature.

The router is thin — it validates input, delegates to a use case from the
composition root, and lets the domain entities/value objects serialize into the
response schemas (Ninja reads attributes off the returned objects).
"""

from __future__ import annotations

from ninja import Router, Status

from src.accounts.adapters.inbound import schemas as s
from src.accounts.application.use_cases import LoginCommand, RegisterCommand
from src.accounts.container import container
from src.shared.infrastructure.auth import AuthPrincipal, JWTAuth

router = Router()
jwt_auth = JWTAuth()


@router.post("/register", response={201: s.UserOut})
def register(request, payload: s.RegisterIn):
    user = container().register_user.execute(RegisterCommand(**payload.model_dump()))
    return Status(201, user)


@router.post("/login", response=s.AuthOut)
def login(request, payload: s.LoginIn):
    result = container().authenticate_user.execute(LoginCommand(**payload.model_dump()))
    return {"user": result.user, "tokens": result.tokens}


@router.post("/refresh", response=s.TokenOut)
def refresh(request, payload: s.RefreshIn):
    return container().refresh_session.execute(payload.refresh_token)


@router.get("/me", auth=jwt_auth, response=s.UserOut)
def me(request):
    principal: AuthPrincipal = request.auth
    return container().get_current_user.execute(principal.id)
