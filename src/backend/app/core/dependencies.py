"""Core dependencies for FastAPI dependency injection."""

from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Request


def get_timezone(request: Request) -> ZoneInfo:
    """
    Dependency to extract timezone from request state.

    The timezone is set by TimeZoneMiddleware from the 'X-Timezone' header.
    Defaults to UTC if not set.

    Usage:
        @router.get("/items")
        async def get_items(timezone: Annotated[ZoneInfo, Depends(get_timezone)]):
            # Use timezone for datetime conversions

    Args:
        request: FastAPI Request object

    Returns:
        ZoneInfo: The timezone for this request
    """
    return getattr(request.state, "timezone", ZoneInfo("UTC"))


TimeZoneDep = Annotated[ZoneInfo, get_timezone]

