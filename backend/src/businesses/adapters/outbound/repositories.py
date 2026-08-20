"""Persistence adapter: maps the Business ORM model to/from the entity."""

from __future__ import annotations

from django.db.models import Q

from src.businesses.adapters.outbound.orm_models import BusinessModel
from src.businesses.domain.entities import Business
from src.businesses.domain.ports import BusinessRepository
from src.shared.domain.values import Page


class DjangoBusinessRepository(BusinessRepository):
    def get_by_id(self, business_id: int) -> Business | None:
        row = BusinessModel.objects.filter(pk=business_id).first()
        return self._to_entity(row) if row else None

    def get_by_slug(self, slug: str) -> Business | None:
        row = BusinessModel.objects.filter(slug=slug).first()
        return self._to_entity(row) if row else None

    def exists_by_slug(self, slug: str) -> bool:
        return BusinessModel.objects.filter(slug=slug).exists()

    def search(
        self,
        query: str,
        page: int,
        page_size: int,
        area: str = "",
        category: str = "",
    ) -> Page[Business]:
        qs = BusinessModel.objects.filter(is_active=True)
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(address__icontains=query))
        if area:
            qs = qs.filter(area=area)
        if category:
            qs = qs.filter(category=category)
        total = qs.count()
        rows = qs.order_by("name")[(page - 1) * page_size : page * page_size]
        return Page(
            items=[self._to_entity(r) for r in rows],
            total=total,
            page=page,
            page_size=page_size,
        )

    def add(self, *, name, slug, description, area, category, address, phone,
            timezone, opens_at, closes_at, created_by) -> Business:
        row = BusinessModel.objects.create(
            name=name,
            slug=slug,
            description=description,
            area=area,
            category=category,
            address=address,
            phone=phone,
            timezone=timezone,
            opens_at=opens_at,
            closes_at=closes_at,
            created_by_id=created_by,
        )
        return self._to_entity(row)

    def update(self, business: Business) -> Business:
        BusinessModel.objects.filter(pk=business.id).update(
            name=business.name,
            slug=business.slug,
            description=business.description,
            area=business.area,
            category=business.category,
            address=business.address,
            phone=business.phone,
            timezone=business.timezone,
            opens_at=business.opens_at,
            closes_at=business.closes_at,
            logo=business.logo_url,
            is_active=business.is_active,
        )
        return self._to_entity(BusinessModel.objects.get(pk=business.id))

    @staticmethod
    def _to_entity(row: BusinessModel) -> Business:
        return Business(
            id=row.pk,
            name=row.name,
            slug=row.slug,
            description=row.description,
            area=row.area,
            category=row.category,
            address=row.address,
            phone=row.phone,
            timezone=row.timezone,
            opens_at=row.opens_at,
            closes_at=row.closes_at,
            logo_url=row.logo,
            is_active=row.is_active,
            created_by=row.created_by_id,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
