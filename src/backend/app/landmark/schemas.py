from uuid import UUID

from fastapi import File, Form, UploadFile
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


class LandmarkCreate(BaseModel):
    """Schema for creating a new landmark with multipart form data support"""

    name: str = Form(..., min_length=1, max_length=255, description="Landmark name")
    description: str | None = Form(
        None, max_length=1000, description="Landmark description"
    )
    latitude: float = Form(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Form(..., ge=-180, le=180, description="Longitude coordinate")
    unlock_radius_meters: int = Form(
        100, ge=1, le=10000, description="Radius in meters for unlocking landmark"
    )
    photo_radius_meters: int = Form(
        50, ge=1, le=5000, description="Radius in meters for taking photos"
    )
    area_id: UUID = Form(..., description="Area ID where landmark is located")
    image_file: UploadFile | None = File(None, description="Landmark image file")

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    @field_validator("image_file", mode="before")
    @classmethod
    def validate_file_fields(cls, v):
        """Convert empty string to None for file upload fields"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @field_validator("area_id", mode="before")
    @classmethod
    def validate_area_id(cls, v):
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
                raise ValueError(f"Invalid UUID format for area_id: {v}") from e

        # Handle any other type
        raise ValueError(
            f"area_id must be a valid UUID or None, got {type(v).__name__}"
        )

    @field_validator("name", "description", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        """Convert empty string to None for string fields"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class LandmarkUpdate(BaseModel):
    """Schema for updating an existing landmark with multipart form data support - all fields optional"""

    name: str | None = Form(
        None, min_length=1, max_length=255, description="Landmark name"
    )
    description: str | None = Form(
        None, max_length=1000, description="Landmark description"
    )
    latitude: float | None = Form(
        None, ge=-90, le=90, description="Latitude coordinate"
    )
    longitude: float | None = Form(
        None, ge=-180, le=180, description="Longitude coordinate"
    )
    unlock_radius_meters: int | None = Form(
        None, ge=1, le=10000, description="Radius in meters for unlocking landmark"
    )
    photo_radius_meters: int | None = Form(
        None, ge=1, le=5000, description="Radius in meters for taking photos"
    )
    area_id: UUID | None = Form(None, description="Area ID where landmark is located")
    image_file: UploadFile | None = File(None, description="Landmark image file")

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    @field_validator("image_file", mode="before")
    @classmethod
    def validate_file_fields(cls, v):
        """Convert empty string to None for file upload fields"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @field_validator("area_id", mode="before")
    @classmethod
    def validate_area_id(cls, v):
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
                raise ValueError(f"Invalid UUID format for area_id: {v}") from e

        # Handle any other type
        raise ValueError(
            f"area_id must be a valid UUID or None, got {type(v).__name__}"
        )

    @field_validator("name", "description", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        """Convert empty strings to None for optional fields"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @field_validator("latitude", "longitude", mode="before")
    @classmethod
    def validate_coordinates(cls, v):
        """Convert empty string to None and validate float values for coordinate fields"""
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        if isinstance(v, str):
            try:
                return float(v.strip())
            except (ValueError, AttributeError) as e:
                raise ValueError(f"Invalid float value for coordinate: {v}") from e
        return v

    @field_validator("unlock_radius_meters", "photo_radius_meters", mode="before")
    @classmethod
    def validate_radius_fields(cls, v):
        """Convert empty string to None and validate int values for radius fields"""
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        if isinstance(v, str):
            try:
                return int(v.strip())
            except (ValueError, AttributeError) as e:
                raise ValueError(f"Invalid integer value for radius: {v}") from e
        return v


class LandmarkResponse(LandmarkBase, TimezoneAwareSchema):
    """Schema for landmark responses - includes all read-only fields with timezone-aware timestamps"""

    id: UUID = Field(..., description="Unique landmark identifier")
    area_id: UUID = Field(..., description="Area ID where landmark is located")
    creator_id: UUID = Field(..., description="User ID who created the landmark")
    image_url: str | None = Field(None, description="URL to landmark image")

    model_config = ConfigDict(from_attributes=True)


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
