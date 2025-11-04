"""Custom response handler that injects timezone context into Pydantic serialization."""

import json
from typing import Any
from zoneinfo import ZoneInfo

from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask


class TimezoneAwareJSONResponse(JSONResponse):
    """
    Custom JSON response that automatically injects timezone context for Pydantic models.

    This response class extracts the timezone from the request state (set by TimeZoneMiddleware)
    and passes it as context to Pydantic's model_dump_json, enabling automatic timezone
    conversion for all schemas that inherit from TimezoneAwareSchema.
    """

    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
        timezone: ZoneInfo | None = None,
    ) -> None:
        """
        Initialize the response with timezone context.

        Args:
            content: Response content (Pydantic model, dict, list, etc.)
            status_code: HTTP status code
            headers: Response headers
            media_type: Media type
            background: Background task
            timezone: Client's timezone for datetime conversion
        """
        self.timezone = timezone or ZoneInfo("UTC")
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )

    def render(self, content: Any) -> bytes:
        """
        Render the response content with timezone context.

        If the content is a Pydantic model, serialize it with timezone context.
        Otherwise, use standard JSON serialization.
        """
        if isinstance(content, BaseModel):
            # Serialize Pydantic model with timezone context
            return content.model_dump_json(
                context={"timezone": self.timezone},
                exclude_none=False,
            ).encode("utf-8")

        # For other types, use default serialization
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")
