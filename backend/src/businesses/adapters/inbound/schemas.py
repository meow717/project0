"""HTTP DTOs for the businesses feature."""

from __future__ import annotations

from datetime import time

from ninja import Schema
from pydantic import Field


class BusinessIn(Schema):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str = Field(default="", max_length=2000)
    area: str = Field(default="", max_length=64)
    category: str = Field(default="", max_length=64)
    address: str = Field(default="", max_length=255)
    phone: str = Field(default="", max_length=64)
    timezone: str = "Asia/Riyadh"
    opens_at: str = "09:00"
    closes_at: str = "17:00"


class BusinessUpdateIn(Schema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    area: str | None = Field(default=None, max_length=64)
    category: str | None = Field(default=None, max_length=64)
    address: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=64)
    timezone: str | None = None
    opens_at: str | None = None
    closes_at: str | None = None


class BusinessOut(Schema):
    id: int
    name: str
    slug: str
    description: str = ""
    area: str = ""
    category: str = ""
    address: str = ""
    phone: str = ""
    timezone: str = "Asia/Riyadh"
    opens_at: time
    closes_at: time
    logo_url: str | None = None
    is_active: bool = True


class LogoOut(Schema):
    logo_url: str
