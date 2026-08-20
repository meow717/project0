"""Create a demo staff user, business and services for local development.

Usage: ``uv run python manage.py seed_demo``

Idempotent: re-running updates the demo business to the current demo identity
(so an old "Demo Clinic" row becomes the coffee shop) and replaces the demo
services.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from src.accounts.adapters.outbound.hasher import DjangoPasswordHasher
from src.accounts.domain.entities import ROLE_STAFF
from src.accounts.models import UserModel
from src.businesses.adapters.outbound.orm_models import BusinessModel

DEMO_SLUG = "coffee"

DEMO_BUSINESS = {
    "name": "Coffee",
    "description": "A specialty coffee shop for local development.",
    "area": "المنصور",
    "category": "مقاهي",
    "address": "Main Street 1",
    "phone": "+966500000000",
    "timezone": "Asia/Riyadh",
}

DEMO_SERVICES = [
    {"name": "Espresso", "ticket_prefix": "A", "avg_duration_sec": 180, "display_order": 1},
    {"name": "Filter Coffee", "ticket_prefix": "B", "avg_duration_sec": 240, "display_order": 2},
]


class Command(BaseCommand):
    help = "Seed a demo business + staff user (idempotent)."

    @transaction.atomic
    def handle(self, *args, **options):  # noqa: ANN002, ANN003
        hasher = DjangoPasswordHasher()
        staff, _ = UserModel.objects.get_or_create(
            email="staff@demo.com",
            defaults={
                "full_name": "Demo Staff",
                "password": hasher.hash("staffpass123"),
                "role": ROLE_STAFF,
            },
        )

        # Reuse the old demo clinic if present so we don't create a duplicate.
        business = BusinessModel.objects.filter(slug=DEMO_SLUG).first() or (
            BusinessModel.objects.filter(slug="demo-clinic").first()
        )
        if business is None:
            business = BusinessModel(slug=DEMO_SLUG, created_by=staff)

        for field, value in DEMO_BUSINESS.items():
            setattr(business, field, value)
        business.slug = DEMO_SLUG
        business.created_by = staff
        business.save()

        staff.business = business
        staff.save(update_fields=["business"])

        # Replace demo services so the menu always matches the coffee shop.
        business.services.all().delete()
        for svc in DEMO_SERVICES:
            business.services.create(**svc)

        self.stdout.write(self.style.SUCCESS("Demo business + services created."))
