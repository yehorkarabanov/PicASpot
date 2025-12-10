from uuid import UUID

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.schemas import BaseReturn
from app.core.schemas_base import TimezoneAwareSchema


class LandmarkBase(BaseModel):
    """Base schema with common landmark attributes"""

    name: str = Field(..., min_length=1, max_length=255, description="Landmark name")
    description: str | None = Field(
        None, max_length=1000, description="Landmark description"
    )
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    unlock_radius_meters: int = Field(
        100, ge=1, le=10000, description="Radius in meters for unlocking landmark"
    )
    photo_radius_meters: int = Field(
        50, ge=1, le=5000, description="Radius in meters for taking photos"
    )


class LandmarkCreate(LandmarkBase):
    """Schema for creating a new landmark"""

    area_id: UUID = Field(..., description="Area ID where landmark is located")
    image_file: UploadFile | None = None

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    @field_validator("image_file", mode="before")
    @classmethod
    def validate_file_fields(cls, v):
        """Convert empty string to None for file upload fields"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class LandmarkUpdate(BaseModel):
    """Schema for updating an existing landmark - all fields optional"""

    name: str | None = Field(
        None, min_length=1, max_length=255, description="Landmark name"
    )
    description: str | None = Field(
        None, max_length=1000, description="Landmark description"
    )
    latitude: float | None = Field(
        None, ge=-90, le=90, description="Latitude coordinate"
    )
    longitude: float | None = Field(
        None, ge=-180, le=180, description="Longitude coordinate"
    )
    unlock_radius_meters: int | None = Field(
        None, ge=1, le=10000, description="Radius in meters for unlocking landmark"
    )
    photo_radius_meters: int | None = Field(
        None, ge=1, le=5000, description="Radius in meters for taking photos"
    )
    area_id: UUID | None = Field(None, description="Area ID where landmark is located")
    image_file: UploadFile | None = None

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    @field_validator("image_file", mode="before")
    @classmethod
    def validate_file_fields(cls, v):
        """Convert empty string to None for file upload fields"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class LandmarkResponse(LandmarkBase, TimezoneAwareSchema):
    """Schema for landmark responses - includes all read-only fields with timezone-aware timestamps"""

    id: UUID = Field(..., description="Unique landmark identifier")
    area_id: UUID = Field(..., description="Area ID where landmark is located")
    creator_id: UUID = Field(..., description="User ID who created the landmark")
    image_url: str | None = Field(None, description="URL to landmark image")


class LandmarkListResponse(TimezoneAwareSchema):
    """Schema for paginated list of landmarks with timezone-aware timestamps"""

    landmarks: list[LandmarkResponse] = Field(
        default_factory=list, description="List of landmarks"
    )
    total: int = Field(..., ge=0, description="Total number of landmarks")


class LandmarkReturn(BaseReturn):
    """API response wrapper for single landmark"""

    data: LandmarkResponse | None = None


class LandmarkListReturn(BaseReturn):
    """API response wrapper for list of landmarks"""

    data: LandmarkListResponse | None = None


class LandmarkNearbyRequest(BaseModel):
    """Schema for finding nearby landmarks"""

    latitude: float = Field(..., ge=-90, le=90, description="Current latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Current longitude")
    radius_meters: int = Field(
        1000, ge=1, le=50000, description="Search radius in meters"
    )
    area_id: UUID | None = Field(
        None, description="Optional area ID to filter landmarks"
    )
    only_verified: bool = Field(
        default=False, description="Only return landmarks from verified areas"
    )
    load_from_same_area: bool = Field(
        default=False,
        description="Load all landmarks from same areas as found landmarks, even outside radius",
    )
