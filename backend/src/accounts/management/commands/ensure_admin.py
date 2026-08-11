"""Idempotently ensure the default admin superuser exists.

Reads ADMIN_EMAIL / ADMIN_PASSWORD / ADMIN_FULL_NAME from settings (env). Safe to
run on every boot — the Docker entrypoint calls it, and a data migration creates
it on the first `migrate`.
"""

from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand

from src.accounts.adapters.outbound.orm_models import UserModel


class Command(BaseCommand):
    help = "Create or update the default admin superuser from settings/env."

    def handle(self, *args, **options) -> None:
        email = settings.ADMIN_EMAIL
        user, created = UserModel.objects.get_or_create(
            email=email,
            defaults={"full_name": settings.ADMIN_FULL_NAME},
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        if not user.full_name:
            user.full_name = settings.ADMIN_FULL_NAME
        # Keep the documented credentials working on every init.
        user.set_password(settings.ADMIN_PASSWORD)
        user.save()
        self.stdout.write(
            self.style.SUCCESS(f"Admin {'created' if created else 'updated'}: {email}")
        )
