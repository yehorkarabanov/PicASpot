"""
Redis-related test fixtures.

This module provides fixtures for Redis client and cleanup utilities.
"""

from collections.abc import AsyncGenerator

import pytest_asyncio

from app.database.redis import get_redis_client, init_redis


@pytest_asyncio.fixture(scope="session")
async def test_redis_client():
    """
    Initialize Redis client for tests.

    The Redis client is initialized once per test session and reused
    across all tests. Individual tests should clean up their data
    using the redis_cleanup fixture.
    """
    await init_redis()
    client = await get_redis_client()
    yield client
    # Session-level cleanup is minimal - per-test cleanup is more important


@pytest_asyncio.fixture(autouse=True)
async def redis_cleanup() -> AsyncGenerator[None, None]:
    """
    Clean Redis data between tests (runs automatically).

    This fixture removes test-related keys from Redis after each test
    to prevent data leakage. It runs automatically for all tests.

    Keys cleaned:
    - token:* (verification and reset tokens)
    - rate_limit:* (rate limiting counters)
    """
    yield

    # Cleanup after test
    redis_client = await get_redis_client()

    # Delete token-related keys
    deleted_count = 0
    async for key in redis_client.scan_iter(match="token:*"):
        await redis_client.delete(key)
        deleted_count += 1

    # Delete rate limit keys
    async for key in redis_client.scan_iter(match="rate_limit:*"):
        await redis_client.delete(key)
        deleted_count += 1


__all__ = ["test_redis_client", "redis_cleanup"]
