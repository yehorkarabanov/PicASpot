"""Base schemas with automatic timezone conversion for datetime fields."""

import datetime
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict


class TimezoneAwareSchema(BaseModel):
    """
    Base schema that automatically converts UTC datetime fields to client's timezone.

    This schema provides utilities for timezone conversion, but the actual conversion
    should happen in the service layer before model validation, not during serialization.

    This approach is cleaner and more predictable than trying to intercept serialization.
    """

    model_config = ConfigDict(
        from_attributes=True,
        # Serialize datetimes as ISO 8601 strings with timezone
        json_encoders={datetime.datetime: lambda v: v.isoformat()},
    )

    @staticmethod
    def convert_timestamps_for_timezone(
        data: dict[str, Any], timezone: ZoneInfo
    ) -> dict[str, Any]:
        """
        Convert all datetime fields in data dict to the specified timezone.

        This should be called in the service layer before model validation.

        Args:
            data: Dictionary containing model data
            timezone: Target timezone for conversion

        Returns:
            Dictionary with converted datetime fields
        """
        if timezone.key == "UTC":
            return data

        converted = {}
        for key, value in data.items():
            if isinstance(value, datetime.datetime):
                # If naive, assume UTC
                if value.tzinfo is None:
                    value = value.replace(tzinfo=ZoneInfo("UTC"))
                # Convert to target timezone
                converted[key] = value.astimezone(timezone)
            else:
                converted[key] = value

        return converted

    @classmethod
    def model_validate_with_timezone(
        cls, obj: Any, timezone: ZoneInfo
    ) -> "TimezoneAwareSchema":
        """
        Validate a model and convert datetime fields to the specified timezone.

        This is a convenience method that combines model validation with timezone conversion.

        Args:
            obj: Object to validate (SQLAlchemy model, dict, etc.)
            timezone: Target timezone for datetime conversion

        Returns:
            Validated model with converted timestamps
        """
        if hasattr(obj, "__dict__"):
            data = {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        elif isinstance(obj, dict):
            data = obj
        else:
            return cls.model_validate(obj)

        # Convert timestamps
        converted_data = cls.convert_timestamps_for_timezone(data, timezone)

        return cls.model_validate(converted_data)


class TimestampMixin(BaseModel):
    """
    Mixin for schemas that include created_at and updated_at fields.

    These fields are automatically converted to the client's timezone
    when the parent schema extends TimezoneAwareSchema.
    """

    created_at: datetime.datetime
    updated_at: datetime.datetime
