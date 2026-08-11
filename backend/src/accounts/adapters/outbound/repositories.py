"""Persistence adapter: maps the Django ORM model to/from the domain entity."""

from __future__ import annotations

from src.accounts.adapters.outbound.orm_models import UserModel
from src.accounts.domain.entities import User
from src.accounts.domain.ports import UserRepository


class DjangoUserRepository(UserRepository):
    def get_by_id(self, user_id: int) -> User | None:
        row = UserModel.objects.filter(pk=user_id).first()
        return self._to_entity(row) if row else None

    def get_by_email(self, email: str) -> User | None:
        row = UserModel.objects.filter(email__iexact=email).first()
        return self._to_entity(row) if row else None

    def exists_by_email(self, email: str) -> bool:
        return UserModel.objects.filter(email__iexact=email).exists()

    def add(self, *, email: str, full_name: str, password_hash: str) -> User:
        # ``password`` stores the hash produced by the PasswordHasher port, which
        # is a valid Django password hash, so admin login stays compatible.
        row = UserModel.objects.create(
            email=email,
            full_name=full_name,
            password=password_hash,
        )
        return self._to_entity(row)

    @staticmethod
    def _to_entity(row: UserModel) -> User:
        return User(
            id=row.pk,
            email=row.email,
            full_name=row.full_name,
            is_active=row.is_active,
            is_staff=row.is_staff,
            password_hash=row.password,
            created_at=row.date_joined,
            updated_at=row.updated_at,
        )
