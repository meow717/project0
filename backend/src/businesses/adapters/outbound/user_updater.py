"""Outbound adapter: promotes a user to staff and links their business.

This keeps the ``created_by`` ownership + role promotion in one place, shared by
the business creation use case and the ``seed_demo`` command.
"""

from __future__ import annotations

from django.db import transaction

from src.accounts.domain.entities import ROLE_STAFF
from src.accounts.models import UserModel


def promote_to_staff(user_id: int, business_id: int) -> None:
    with transaction.atomic():
        UserModel.objects.filter(pk=user_id).update(
            role=ROLE_STAFF,
            business_id=business_id,
        )
