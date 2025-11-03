from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.database.redis import get_redis_client


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 10, time_window: int = 60, paths: list[str] = None):
        super().__init__(app)
        self.max_requests = max_requests
        self.time_window = time_window
        self.paths = paths

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        print(f"Rate limiting check for IP: {request.client.host} on path: {request.url.path}")

        if request.url.path in self.paths:
            redis_client = await get_redis_client()
            ip = request.client.host
            key = f"rate_limit:{ip}:{request.url.path}"

            async with redis_client.pipeline() as pipe:
                await pipe.incr(key)
                await pipe.expire(key, self.time_window, nx=True)
                current, _ = await pipe.execute()

            if current > self.max_requests:
                return Response("Rate limited", status_code=429)

        response = await call_next(request)
        return response
