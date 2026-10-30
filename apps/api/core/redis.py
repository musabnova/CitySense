import logging
from apps.api.core.config import settings

logger = logging.getLogger(__name__)

class AsyncRedisProxy:
    """Asynchronous Redis client proxy with high-resilience in-memory fallback."""
    def __init__(self, url: str):
        self.url = url
        self._client = None
        self._memory_store = {}

    async def get_client(self):
        try:
            import redis.asyncio as aioredis
            if not self._client:
                self._client = aioredis.from_url(self.url, socket_timeout=2)
                await self._client.ping()
            return self._client
        except Exception as e:
            logger.info(f"External Redis broker unavailable ({e}). Using async in-memory broker cache.")
            return None

    async def ping(self) -> bool:
        client = await self.get_client()
        if client:
            try:
                return await client.ping()
            except Exception:
                return False
        return True # In-memory proxy ping passes

    async def set(self, key: str, value: str, ex: int = None):
        client = await self.get_client()
        if client:
            return await client.set(key, value, ex=ex)
        self._memory_store[key] = value
        return True

    async def get(self, key: str):
        client = await self.get_client()
        if client:
            return await client.get(key)
        return self._memory_store.get(key)

redis_client = AsyncRedisProxy(settings.REDIS_URL)

async def check_redis_health() -> dict:
    is_live = await redis_client.ping()
    is_external = (await redis_client.get_client()) is not None
    return {
        "status": "healthy" if is_live else "degraded",
        "url": settings.REDIS_URL,
        "is_connected": is_external,
        "mode": "standalone_redis" if is_external else "in_memory_async_fallback"
    }

