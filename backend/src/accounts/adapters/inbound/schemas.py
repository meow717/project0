"""HTTP DTOs (django-ninja / Pydantic schemas) for the accounts API."""

from __future__ import annotations

from ninja import Schema
from pydantic import EmailStr, Field


class RegisterIn(Schema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)


class LoginIn(Schema):
    email: EmailStr
    password: str


class RefreshIn(Schema):
    refresh_token: str


class UserOut(Schema):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    is_staff: bool


class TokenOut(Schema):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class AuthOut(Schema):
    user: UserOut
    tokens: TokenOut
