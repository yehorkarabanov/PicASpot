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

    model_config = ConfigDict(extra="forbid")

    @field_validator("parent_area_id", mode="before")
    @classmethod
    def validate_parent_area_id(cls, v):
        """Convert empty string to None for optional UUID field"""
        if v == "" or v is None:
            return None
        return v


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
