"""Base schemas with automatic timezone conversion for datetime fields."""

import datetime
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, model_serializer


class TimezoneAwareSchema(BaseModel):
    """
    Base schema that automatically converts UTC datetime fields to client's timezone.

    This should be used for response schemas that include datetime fields.
    The timezone is injected via context during serialization.

    The conversion happens automatically during JSON serialization when the
    response is returned from FastAPI endpoints. The timezone is read from
    the serialization context which is set by the custom response handler.

    All datetime fields in the schema and nested schemas are automatically
    converted from UTC to the client's timezone.
    """

    model_config = ConfigDict(
        from_attributes=True,
        # Serialize datetimes as ISO 8601 strings with timezone
        json_encoders={datetime.datetime: lambda v: v.isoformat()}
    )

    @model_serializer(mode='wrap', when_used='json')
    def _serialize_with_timezone(self, serializer: Any, info: Any) -> dict[str, Any]:
        """
        Wrap the default serializer to convert datetime fields to client timezone.

        This runs during JSON serialization (API responses) and converts all
        datetime fields from UTC to the client's timezone specified in context.
        """
        # Get the default serialized data
        data = serializer(self)

        # Get timezone from context, default to UTC if not provided
        timezone = ZoneInfo("UTC")
        if info.context:
            timezone = info.context.get("timezone", ZoneInfo("UTC"))

        # Only convert if timezone is not UTC
        if timezone.key != "UTC":
            data = self._convert_datetimes_recursive(data, timezone)

        return data

    @staticmethod
    def _convert_datetimes_recursive(obj: Any, timezone: ZoneInfo) -> Any:
        """
        Recursively convert all datetime objects in a structure to the target timezone.

        Handles:
        - Direct datetime objects
        - Dictionaries with datetime values
        - Lists with datetime values
        - Nested structures
        """
        if isinstance(obj, datetime.datetime):
            # If naive (from database), assume UTC
            if obj.tzinfo is None:
                obj = obj.replace(tzinfo=ZoneInfo("UTC"))
            # Convert to target timezone
            return obj.astimezone(timezone)

        elif isinstance(obj, dict):
            return {
                key: TimezoneAwareSchema._convert_datetimes_recursive(value, timezone)
                for key, value in obj.items()
            }

        elif isinstance(obj, list):
            return [
                TimezoneAwareSchema._convert_datetimes_recursive(item, timezone)
                for item in obj
            ]

        return obj


class TimestampMixin(BaseModel):
    """
    Mixin for schemas that include created_at and updated_at fields.

    These fields are automatically converted to the client's timezone
    when the parent schema extends TimezoneAwareSchema.
    """
    created_at: datetime.datetime
    updated_at: datetime.datetime

