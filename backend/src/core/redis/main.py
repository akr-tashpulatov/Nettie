import json

import redis.asyncio as redis

from src.core.config import settings
from src.core.logger import logging


class RedisService:
    def __init__(self):
        self._client = redis.Redis(
            host=settings.REDIS_HOST,
            password=settings.REDIS_PASSWORD,
            port=settings.REDIS_PORT,
            decode_responses=True,
        )

    async def get(self, key: str) -> bytes | str | None:
        """Fetch data from the redis."""
        try:
            data = await self._client.get(key)
            if not data:
                return None
            try:
                return json.loads(data)
            except Exception:
                return data
        except redis.RedisError as e:
            logging.error(f"Redis GET error for key '{key}': {e}")
            return None

    async def set(
        self, key: str, value: str | int | bytes | dict, ttl: int | None = None
    ) -> bool:
        """Store data in the redis with a TTL."""
        try:
            await self._client.set(key, value, ex=ttl)
            return True
        except redis.RedisError as e:
            logging.error(f"Redis SET error for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete data in the redis by key."""
        try:
            count = await self._client.delete(key)
            return count > 0
        except redis.RedisError as e:
            logging.error(f"Redis DELETE error for key '{key}': {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if data exists in the redis by key."""
        try:
            count = await self._client.exists(key)
            return count == 1
        except redis.RedisError as e:
            logging.error(f"Redis EXISTS error for key '{key}': {e}")
            return False

    async def ttl(self, key: str) -> int:
        """Return remaining TTL in seconds. 0 if key is missing or has no expiry."""
        try:
            remaining = await self._client.ttl(key)
            return remaining if remaining > 0 else 0
        except redis.RedisError as e:
            logging.error(f"Redis TTL error for key '{key}': {e}")
            return 0

    async def incr(self, key: str) -> int:
        """Atomically increment the integer stored at key and return the new value."""
        try:
            return await self._client.incr(key)
        except redis.RedisError as e:
            logging.error(f"Redis INCR error for key '{key}': {e}")
            return 0

    async def expire(self, key: str, ttl: int) -> bool:
        """Set a TTL (seconds) on an existing key."""
        try:
            return bool(await self._client.expire(key, ttl))
        except redis.RedisError as e:
            logging.error(f"Redis EXPIRE error for key '{key}': {e}")
            return False

    async def sadd(self, key: str, member: str) -> bool:
        """Add a member to the set stored at key."""
        try:
            return bool(await self._client.sadd(key, member))
        except redis.RedisError as e:
            logging.error(f"Redis SADD error for key '{key}': {e}")
            return False

    async def srem(self, key: str, member: str) -> bool:
        """Remove a member from the set stored at key."""
        try:
            return bool(await self._client.srem(key, member))
        except redis.RedisError as e:
            logging.error(f"Redis SREM error for key '{key}': {e}")
            return False

    async def sismember(self, key: str, member: str) -> bool:
        """Check whether member is part of the set stored at key."""
        try:
            return bool(await self._client.sismember(key, member))
        except redis.RedisError as e:
            logging.error(f"Redis SISMEMBER error for key '{key}': {e}")
            return False


redis_service = RedisService()
