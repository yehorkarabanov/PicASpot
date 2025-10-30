from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import BaseReturn


class AreaBase(BaseModel):
    """Base schema with common area attributes"""

    name: str = Field(..., min_length=1, max_length=255, description="Area name")
    description: str | None = Field(
        None, max_length=1000, description="Area description"
    )
    image_url: str | None = Field(None, max_length=500, description="URL to area image")
    badge_url: str | None = Field(None, max_length=500, description="URL to area badge")


class AreaCreate(AreaBase):
    """Schema for creating a new area"""

    parent_area_id: UUID | None = Field(
        None, description="Parent area ID for hierarchical structure"
    )
    # created_by will be injected from authenticated user, not from request body


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


class AreaResponse(AreaBase):
    """Schema for area responses - includes all read-only fields"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique area identifier")
    parent_area_id: UUID | None = Field(None, description="Parent area ID")
    is_verified: bool = Field(False, description="Whether area is verified")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class AreaListResponse(BaseModel):
    """Schema for paginated list of areas"""

    model_config = ConfigDict(from_attributes=True)

    areas: list[AreaResponse] = Field(default_factory=list, description="List of areas")
    total: int = Field(..., ge=0, description="Total number of areas")


class AreaReturn(BaseReturn):
    """API response wrapper for single area"""

    data: AreaResponse | None = None


class AreaListReturn(BaseReturn):
    """API response wrapper for list of areas"""

    data: AreaListResponse | None = None
