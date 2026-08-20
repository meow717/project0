"""Application use cases for the businesses feature."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import time

from src.businesses.domain.entities import Business
from src.businesses.domain.exceptions import (
    BusinessNotFound,
    InvalidBusinessData,
    SlugAlreadyUsed,
)
from src.businesses.domain.ports import BusinessRepository
from src.shared.application.use_case import UseCase
from src.shared.domain.ports import Clock, FileStorage
from src.shared.domain.timezones import resolve_zone
from src.shared.domain.values import Page


# --------------------------------------------------------------------------- #
# Commands / results
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class CreateBusinessCommand:
    name: str
    slug: str
    created_by: int
    description: str = ""
    area: str = ""
    category: str = ""
    address: str = ""
    phone: str = ""
    timezone: str = "Asia/Riyadh"
    opens_at: time = time(9, 0)
    closes_at: time = time(17, 0)


@dataclass(frozen=True)
class UpdateBusinessCommand:
    business_id: int
    name: str | None = None
    description: str | None = None
    area: str | None = None
    category: str | None = None
    address: str | None = None
    phone: str | None = None
    timezone: str | None = None
    opens_at: time | None = None
    closes_at: time | None = None


@dataclass(frozen=True)
class UploadLogoCommand:
    business_id: int
    content: bytes
    content_type: str
    filename: str


_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")


class CreateBusiness(UseCase[CreateBusinessCommand, Business]):
    def __init__(self, businesses: BusinessRepository) -> None:
        self._businesses = businesses

    def execute(self, data: CreateBusinessCommand) -> Business:
        slug = _slugify(data.slug)
        if not _SLUG_RE.match(slug):
            raise InvalidBusinessData("Slug must be URL-safe lowercase letters, digits and dashes")
        if self._businesses.exists_by_slug(slug):
            raise SlugAlreadyUsed()
        if data.opens_at >= data.closes_at:
            raise InvalidBusinessData("opens_at must be before closes_at")
        resolve_zone(data.timezone)  # validates the IANA name
        return self._businesses.add(
            name=data.name.strip(),
            slug=slug,
            description=data.description.strip(),
            area=data.area.strip(),
            category=data.category.strip(),
            address=data.address.strip(),
            phone=data.phone.strip(),
            timezone=data.timezone,
            opens_at=data.opens_at,
            closes_at=data.closes_at,
            created_by=data.created_by,
        )


class UpdateBusiness(UseCase[UpdateBusinessCommand, Business]):
    def __init__(self, businesses: BusinessRepository) -> None:
        self._businesses = businesses

    def execute(self, data: UpdateBusinessCommand) -> Business:
        business = self._businesses.get_by_id(data.business_id)
        if business is None:
            raise BusinessNotFound()

        if data.name is not None:
            business.name = data.name.strip()
        if data.description is not None:
            business.description = data.description.strip()
        if data.area is not None:
            business.area = data.area.strip()
        if data.category is not None:
            business.category = data.category.strip()
        if data.address is not None:
            business.address = data.address.strip()
        if data.phone is not None:
            business.phone = data.phone.strip()
        if data.timezone is not None:
            resolve_zone(data.timezone)
            business.timezone = data.timezone
        if data.opens_at is not None:
            business.opens_at = data.opens_at
        if data.closes_at is not None:
            business.closes_at = data.closes_at
        if business.opens_at >= business.closes_at:
            raise InvalidBusinessData("opens_at must be before closes_at")

        return self._businesses.update(business)


class GetBusinessBySlug(UseCase[str, Business]):
    def __init__(self, businesses: BusinessRepository) -> None:
        self._businesses = businesses

    def execute(self, slug: str) -> Business:
        business = self._businesses.get_by_slug(slug)
        if business is None or not business.is_active:
            raise BusinessNotFound()
        return business


class GetBusiness(UseCase[int, Business]):
    def __init__(self, businesses: BusinessRepository) -> None:
        self._businesses = businesses

    def execute(self, business_id: int) -> Business:
        business = self._businesses.get_by_id(business_id)
        if business is None:
            raise BusinessNotFound()
        return business


class SearchBusinesses(UseCase[tuple[str, str, str, int, int], Page[Business]]):
    def __init__(self, businesses: BusinessRepository) -> None:
        self._businesses = businesses

    def execute(self, data: tuple[str, str, str, int, int]) -> Page[Business]:
        query, area, category, page, page_size = data
        return self._businesses.search(query.strip(), page, page_size, area, category)


class UploadBusinessLogo(UseCase[UploadLogoCommand, Business]):
    def __init__(self, businesses: BusinessRepository, storage: FileStorage, clock: Clock) -> None:
        self._businesses = businesses
        self._storage = storage
        self._clock = clock

    def execute(self, data: UploadLogoCommand) -> Business:
        business = self._businesses.get_by_id(data.business_id)
        if business is None:
            raise BusinessNotFound()

        # Replace any existing logo.
        if business.logo_url:
            self._storage.delete(business.logo_url)

        safe = re.sub(r"[^a-zA-Z0-9_.-]", "_", data.filename or "logo")
        key = f"businesses/{data.business_id}/{self._clock.now().timestamp():.0f}-{safe}"
        url = self._storage.save(key, data.content, data.content_type)
        business.logo_url = url
        return self._businesses.update(business)
