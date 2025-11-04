from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.utils import get_timezone_from_header


class TimeZoneMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle timezone settings for incoming requests.

    Extracts timezone from the 'X-Timezone' header (e.g., 'America/New_York', 'Europe/London')
    and stores it in request.state for use by dependencies and repositories.

    If no timezone is provided or invalid, defaults to UTC.
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract timezone from header, default to UTC if not provided or invalid
        timezone_str = request.headers.get("X-Timezone", "UTC")
        timezone = get_timezone_from_header(timezone_str)

        # Store timezone in request state for access in dependencies
        request.state.timezone = timezone

        response = await call_next(request)
        return response
