"""Cache adapter: wraps Django's cache framework behind the ``CachePort``.

Dev uses the ``LocMemCache`` configured in ``settings.dev``; prod uses the
``django_redis.RedisCache`` configured in ``settings.prod``. The swap is purely
a settings change — this adapter never knows which backend it is on.
"""

from __future__ import annotations

from django.core.cache import cache

from src.shared.domain.ports import CachePort


class DjangoCacheAdapter(CachePort):
    def get(self, key: str) -> str | None:
        value = cache.get(key)
        return value if isinstance(value, str) else None

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        cache.set(key, value, timeout=ttl_seconds)

    def delete(self, key: str) -> None:
        cache.delete(key)
