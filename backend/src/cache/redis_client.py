"""
Redis client module for Ras's Deep Treasure backend.

Provides singleton Redis connection pool with helper methods.
Constitution: Explicit connection management with proper lifecycle handling.
"""

import json
from typing import Any

import redis.asyncio as aioredis
from redis.asyncio import Redis

from src.config import get_settings

# Global Redis client (initialized at app startup)
redis_client: Redis | None = None


async def init_redis() -> None:
    """
    Initialize Redis connection pool.

    Must be called during application startup (lifespan context).
    """
    global redis_client
    settings = get_settings()

    redis_client = await aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=settings.redis_max_connections,
    )


async def close_redis() -> None:
    """
    Close Redis connection pool.

    Must be called during application shutdown (lifespan context).
    """
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


def get_redis() -> Redis:
    """
    Get Redis client instance.

    Returns:
        Redis: Active Redis client.

    Raises:
        RuntimeError: If Redis client is not initialized.
    """
    if redis_client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis() at app startup.")
    return redis_client


async def get_value(key: str) -> str | None:
    """
    Get value from Redis.

    Args:
        key: Redis key.

    Returns:
        Value as string, or None if key doesn't exist.
    """
    client = get_redis()
    return await client.get(key)


async def set_value(key: str, value: str, expire_seconds: int | None = None) -> None:
    """
    Set value in Redis.

    Args:
        key: Redis key.
        value: Value to store.
        expire_seconds: Optional TTL in seconds.
    """
    client = get_redis()
    await client.set(key, value, ex=expire_seconds)


async def delete_value(key: str) -> None:
    """
    Delete value from Redis.

    Args:
        key: Redis key to delete.
    """
    client = get_redis()
    await client.delete(key)


async def get_json(key: str) -> dict[str, Any] | None:
    """
    Get JSON value from Redis.

    Args:
        key: Redis key.

    Returns:
        Parsed JSON dict, or None if key doesn't exist.
    """
    value = await get_value(key)
    return json.loads(value) if value else None


async def set_json(key: str, value: dict[str, Any], expire_seconds: int | None = None) -> None:
    """
    Set JSON value in Redis.

    Args:
        key: Redis key.
        value: Dict to serialize as JSON.
        expire_seconds: Optional TTL in seconds.
    """
    await set_value(key, json.dumps(value), expire_seconds)


async def publish(channel: str, message: str) -> None:
    """
    Publish message to Redis pub/sub channel.

    Args:
        channel: Channel name.
        message: Message to publish.
    """
    client = get_redis()
    await client.publish(channel, message)


async def exists(key: str) -> bool:
    """
    Check if key exists in Redis.

    Args:
        key: Redis key.

    Returns:
        True if key exists, False otherwise.
    """
    client = get_redis()
    return await client.exists(key) > 0
