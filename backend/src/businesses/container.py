"""Composition root for the businesses feature (wires adapters to use cases)."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from src.businesses.adapters.outbound.repositories import DjangoBusinessRepository
from src.businesses.adapters.outbound.user_updater import promote_to_staff
from src.businesses.application.use_cases import (
    CreateBusiness,
    GetBusiness,
    GetBusinessBySlug,
    SearchBusinesses,
    UpdateBusiness,
    UploadBusinessLogo,
)
from src.shared.domain.ports import Clock, FileStorage, SystemClock
from src.shared.infrastructure.storage import DjangoStorageAdapter


class BusinessesContainer:
    def __init__(self) -> None:
        self.businesses = DjangoBusinessRepository()
        self.clock: Clock = SystemClock()
        self.storage: FileStorage = DjangoStorageAdapter()

    @property
    def create_business(self):
        """Create the business and promote the owner to staff of it."""
        inner = CreateBusiness(self.businesses)

        def _execute(data) -> Any:
            business = inner.execute(data)
            promote_to_staff(data.created_by, business.id)
            return business

        return _execute

    @property
    def update_business(self) -> UpdateBusiness:
        return UpdateBusiness(self.businesses)

    @property
    def get_business_by_slug(self) -> GetBusinessBySlug:
        return GetBusinessBySlug(self.businesses)

    @property
    def get_business(self) -> GetBusiness:
        return GetBusiness(self.businesses)

    @property
    def search_businesses(self) -> SearchBusinesses:
        return SearchBusinesses(self.businesses)

    @property
    def upload_business_logo(self) -> UploadBusinessLogo:
        return UploadBusinessLogo(self.businesses, self.storage, self.clock)


@lru_cache(maxsize=1)
def container() -> BusinessesContainer:
    return BusinessesContainer()
