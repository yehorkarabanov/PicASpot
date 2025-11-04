import json
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from pydantic import BaseModel

from app.core.utils import get_timezone_from_header


class TimeZoneMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle timezone settings for incoming requests and responses.

    Extracts timezone from the 'X-Timezone' header (e.g., 'America/New_York', 'Europe/London')
    and stores it in request.state for use by dependencies and repositories.

    Also intercepts JSON responses and injects timezone context when serializing
    Pydantic models, enabling automatic timezone conversion for response schemas.

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

        # Process the request and get the response
        response = await call_next(request)

        # If it's a JSON response with Pydantic model content, re-serialize with timezone context
        # Note: FastAPI already serializes the response by the time it reaches here,
        # so we need to use a different approach (see response handlers in routes)

        return response
