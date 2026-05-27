"""In-memory feature registry with cache and TTL-based invalidation."""

import time
from typing import Optional

from sqlalchemy import select

from lucky_number.database.engine import async_session_factory
from lucky_number.database.models.feature_toggle import FeatureToggle


class FeatureRegistry:
    """Singleton in-memory cache of feature toggle states.

    Features are loaded on startup and cached with configurable TTL (default 60s).
    Cache is invalidated when an admin toggles a feature via the API.
    """

    _instance: Optional["FeatureRegistry"] = None
    _cache: dict[str, bool] = {}
    _last_load: float = 0
    _ttl: int = 60

    def __new__(cls, ttl: int = 60) -> "FeatureRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._ttl = ttl
            cls._instance._cache = {}
            cls._instance._last_load = 0
        return cls._instance

    async def is_active(self, slug: str) -> bool:
        """Check if a feature is active, loading from DB if cache expired."""
        if time.time() - self._last_load > self._ttl:
            await self._load_all()
        return self._cache.get(slug, False)

    async def _load_all(self) -> None:
        """Load all feature states from database into cache."""
        async with async_session_factory() as session:
            result = await session.execute(
                select(FeatureToggle.slug, FeatureToggle.ativa)
            )
            self._cache = {row[0]: row[1] for row in result}
            self._last_load = time.time()

    def invalidate(self) -> None:
        """Force cache invalidation (called after toggle change)."""
        self._last_load = 0

    async def refresh(self) -> None:
        """Force immediate reload from database."""
        await self._load_all()
