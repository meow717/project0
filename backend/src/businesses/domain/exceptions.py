"""Business domain exceptions (subclass the shared hierarchy)."""

from __future__ import annotations

from src.shared.domain.exceptions import ConflictError, NotFoundError, ValidationError


class BusinessNotFound(NotFoundError):
    code = "business_not_found"


class SlugAlreadyUsed(ConflictError):
    code = "slug_already_used"


class InvalidBusinessData(ValidationError):
    code = "invalid_business_data"
