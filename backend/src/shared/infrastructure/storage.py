"""Storage adapter: wraps Django's ``default_storage`` behind ``FileStorage``.

Dev uses the ``FileSystemStorage`` configured in ``settings.dev``; prod uses the
``S3Storage`` (MinIO) configured in ``settings.prod``. Like the cache, the swap
is purely a settings change.
"""

from __future__ import annotations

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from src.shared.domain.ports import FileStorage


class DjangoStorageAdapter(FileStorage):
    def save(self, name: str, content: bytes, content_type: str) -> str:
        path = default_storage.save(name, ContentFile(content))
        return default_storage.url(path)

    def url(self, name: str) -> str:
        return default_storage.url(name)

    def delete(self, name: str) -> None:
        default_storage.delete(name)
