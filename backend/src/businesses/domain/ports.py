"""Driven ports for the businesses feature."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.businesses.domain.entities import Business
from src.shared.domain.values import Page


class BusinessRepository(ABC):
    @abstractmethod
    def get_by_id(self, business_id: int) -> Business | None: ...

    @abstractmethod
    def get_by_slug(self, slug: str) -> Business | None: ...

    @abstractmethod
    def exists_by_slug(self, slug: str) -> bool: ...

    @abstractmethod
    def search(
        self,
        query: str,
        page: int,
        page_size: int,
        area: str = "",
        category: str = "",
    ) -> Page[Business]: ...

    @abstractmethod
    def add(self, *, name: str, slug: str, description: str, area: str,
            category: str, address: str, phone: str, timezone: str,
            opens_at, closes_at, created_by: int) -> Business: ...

    @abstractmethod
    def update(self, business: Business) -> Business: ...
