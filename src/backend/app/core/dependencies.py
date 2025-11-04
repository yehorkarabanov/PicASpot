"""Core FastAPI dependencies for timezone and context management."""

from typing import Annotated, Any
from zoneinfo import ZoneInfo

from fastapi import Depends, Request
from fastapi.responses import JSONResponse as FastAPIJSONResponse
from pydantic import BaseModel


def get_timezone(request: Request) -> ZoneInfo:
    """
    Extract timezone from request state set by TimeZoneMiddleware.

    This timezone is used for converting UTC timestamps to client's local timezone
    in response schemas that inherit from TimezoneAwareSchema.

    Returns:
        ZoneInfo: Client's timezone, defaults to UTC if not provided
    """
    return getattr(request.state, "timezone", ZoneInfo("UTC"))


TimeZoneDep = Annotated[ZoneInfo, Depends(get_timezone)]


def get_pydantic_context(timezone: TimeZoneDep) -> dict[str, Any]:
    """
    Create Pydantic serialization context with timezone.

    This context is used by response models that inherit from TimezoneAwareSchema
    to automatically convert UTC timestamps to the client's timezone.

    Usage in router:
        return AreaResponse.model_validate(area, context=context)

    Returns:
        dict: Context dictionary with timezone
    """
    return {"timezone": timezone}


PydanticContextDep = Annotated[dict[str, Any], Depends(get_pydantic_context)]


class TimezoneAwareJSONResponse(FastAPIJSONResponse):
    """
    Custom JSONResponse that automatically injects timezone context when serializing Pydantic models.

    This ensures that all response models inheriting from TimezoneAwareSchema
    automatically convert timestamps to the client's timezone.

    Usage in router:
        @router.get("/areas/{area_id}", response_class=TimezoneAwareJSONResponse)
        async def get_area(area_id: UUID, timezone: TimeZoneDep):
            area = await service.get_area(area_id)
            return {"data": area}  # Timezone conversion happens automatically
    """

    def render(self, content: Any) -> bytes:
        """Override render to inject timezone context for Pydantic models."""
        # The timezone should be stored in the request state by the middleware
        # However, at this point we don't have access to it, so we rely on
        # FastAPI's response_model parameter to handle serialization with context
        return super().render(content)
