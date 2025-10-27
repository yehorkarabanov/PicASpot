import redis.asyncio as redis

from app.settings import settings

redis_client: redis.Redis | None = None


async def init_redis():
    """Initialize Redis client at startup"""
    global redis_client
    redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


async def close_redis():
    """Close Redis connection on shutdown"""
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None


async def get_redis_client() -> redis.Redis:
    """Get Redis client as a dependency"""
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client


async def check_redis_health() -> bool:
    """Check if Redis is healthy"""
    try:
        if redis_client is None:
            return False
        await redis_client.ping()
        return True
    except Exception:
        return False
