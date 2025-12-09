from datetime import datetime
from uuid import UUID

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.schemas import BaseReturn
from app.core.schemas_base import TimezoneAwareSchema


class AreaBase(BaseModel):
    """Base schema with common area attributes"""

    name: str = Field(..., min_length=1, max_length=255, description="Area name")
    description: str | None = Field(
        None, max_length=1000, description="Area description"
    )


class AreaCreate(AreaBase):
    """Schema for creating a new area"""

    image_file: UploadFile | None = None
    badge_file: UploadFile | None = None
    parent_area_id: UUID | None = Field(
        None, description="Parent area ID for hierarchical structure"
    )

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    @field_validator("parent_area_id", mode="before")
    @classmethod
    def validate_parent_area_id(cls, v):
        """Convert empty string to None and validate UUID format"""
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None

        # If it's already a UUID object, return it
        if isinstance(v, UUID):
            return v

        # Try to convert string to UUID to validate format
        if isinstance(v, str):
            try:
                return UUID(v.strip())
            except (ValueError, AttributeError) as e:
                raise ValueError(f"Invalid UUID format for parent_area_id: {v}") from e

        # Handle any other type
        raise ValueError(f"parent_area_id must be a valid UUID or None, got {type(v).__name__}")


class AreaUpdate(BaseModel):
    """Schema for updating an existing area - all fields optional"""

    name: str | None = Field(
        None, min_length=1, max_length=255, description="Area name"
    )
    description: str | None = Field(
        None, max_length=1000, description="Area description"
    )
    image_url: str | None = Field(None, max_length=500, description="URL to area image")
    badge_url: str | None = Field(None, max_length=500, description="URL to area badge")
    parent_area_id: UUID | None = Field(None, description="Parent area ID")


class AreaResponse(AreaBase, TimezoneAwareSchema):
    """Schema for area responses - includes all read-only fields with timezone-aware timestamps"""

    id: UUID = Field(..., description="Unique area identifier")
    parent_area_id: UUID | None = Field(None, description="Parent area ID")
    is_verified: bool = Field(False, description="Whether area is verified")
    image_url: str | None = Field(None, description="URL to area image")
    badge_url: str | None = Field(None, description="URL to area badge")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class AreaListResponse(TimezoneAwareSchema):
    """Schema for paginated list of areas with timezone-aware timestamps"""

    areas: list[AreaResponse] = Field(default_factory=list, description="List of areas")
    total: int = Field(..., ge=0, description="Total number of areas")


class AreaReturn(BaseReturn):
    """API response wrapper for single area"""

    data: AreaResponse | None = None


class AreaListReturn(BaseReturn):
    """API response wrapper for list of areas"""

    data: AreaListResponse | None = None
