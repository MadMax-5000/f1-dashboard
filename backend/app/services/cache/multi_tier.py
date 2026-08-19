import json
import structlog
import pickle
from typing import Any, Callable, TypeVar
from datetime import timedelta
from functools import wraps

logger = structlog.get_logger()

T = TypeVar("T")


class CacheTier:
    memory: dict[str, Any] = {}
    memory_ttl: dict[str, float] = {}


class MultiTierCache:
    def __init__(self, redis_client=None):
        self._redis = redis_client
        self._local = CacheTier()
        self._stats = {"hits": 0, "misses": 0, "local_hits": 0, "redis_hits": 0}

    async def get(self, key: str, default: T | None = None) -> Any:
        import time

        now = time.monotonic()
        if key in self._local.memory:
            if now < self._local.memory_ttl.get(key, 0):
                self._stats["hits"] += 1
                self._stats["local_hits"] += 1
                return self._local.memory[key]
            else:
                del self._local.memory[key]
                del self._local.memory_ttl[key]
        if self._redis:
            try:
                val = await self._redis.get(key)
                if val:
                    data = pickle.loads(val)
                    self._stats["hits"] += 1
                    self._stats["redis_hits"] += 1
                    return data
            except Exception as e:
                logger.warning("redis_cache_error", key=key, error=str(e))
        self._stats["misses"] += 1
        return default

    async def set(
        self,
        key: str,
        value: Any,
        ttl: timedelta = timedelta(seconds=60),
        tier: str = "all",
    ):
        if tier in ("local", "all"):
            import time

            self._local.memory[key] = value
            self._local.memory_ttl[key] = time.monotonic() + ttl.total_seconds()
        if tier in ("redis", "all") and self._redis:
            try:
                await self._redis.setex(key, int(ttl.total_seconds()), pickle.dumps(value))
            except Exception as e:
                logger.warning("redis_cache_set_error", key=key, error=str(e))

    async def delete(self, key: str):
        self._local.memory.pop(key, None)
        self._local.memory_ttl.pop(key, None)
        if self._redis:
            await self._redis.delete(key)

    async def delete_pattern(self, pattern: str):
        import re

        regex = re.compile(pattern.replace("*", ".*"))
        keys = [k for k in self._local.memory if regex.match(k)]
        for k in keys:
            self._local.memory.pop(k, None)
            self._local.memory_ttl.pop(k, None)
        if self._redis:
            cursor = 0
            while True:
                cursor, keys = await self._redis.scan(cursor, match=pattern, count=100)
                if keys:
                    await self._redis.delete(*keys)
                if cursor == 0:
                    break

    @property
    def stats(self) -> dict:
        total = self._stats["hits"] + self._stats["misses"]
        return {
            **self._stats,
            "hit_rate": self._stats["hits"] / max(total, 1),
            "local_size": len(self._local.memory),
        }

    async def invalidate_all(self):
        self._local.memory.clear()
        self._local.memory_ttl.clear()
        if self._redis:
            await self._redis.flushdb()
        logger.info("cache_invalidated_all")


def cached(cache: MultiTierCache, ttl: timedelta = timedelta(seconds=30)):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__module__}:{func.__name__}:{hash(frozenset(kwargs.items()))}"
            result = await cache.get(key)
            if result is not None:
                return result
            result = await func(*args, **kwargs)
            await cache.set(key, result, ttl=ttl)
            return result

        return wrapper

    return decorator


def memoize(ttl_seconds: float = 30.0):
    def decorator(func):
        cache: dict[str, tuple[Any, float]] = {}
        import time

        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__module__}:{func.__name__}:{hash(frozenset(kwargs.items()))}"
            now = time.monotonic()
            if key in cache:
                val, ts = cache[key]
                if now - ts < ttl_seconds:
                    return val
            result = await func(*args, **kwargs)
            cache[key] = (result, now)
            return result

        return wrapper

    return decorator
