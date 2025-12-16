from typing import TYPE_CHECKING
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.schemas import BaseReturn
from app.core.schemas_base import TimezoneAwareSchema

if TYPE_CHECKING:
    from .models import Landmark


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
    photo_location_radius: int | None = Field(
        None,
        ge=1,
        le=5000,
        description="Radius in meters for taking photos from the specific photo location",
    )
    hint_image_url: str | None = Field(None, description="URL to landmark hint image")
    photo_latitude: float | None = Field(
        None, ge=-90, le=90, description="Latitude coordinate for photo location"
    )
    photo_longitude: float | None = Field(
        None, ge=-180, le=180, description="Longitude coordinate for photo location"
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
    photo_location_radius: int | None = Form(
        None,
        ge=1,
        le=5000,
        description="Radius in meters for taking photos from the specific photo location",
    )
    photo_latitude: float | None = Form(
        None, ge=-90, le=90, description="Latitude coordinate for photo location"
    )
    photo_longitude: float | None = Form(
        None, ge=-180, le=180, description="Longitude coordinate for photo location"
    )
    area_id: UUID = Form(..., description="Area ID where landmark is located")
    image_file: UploadFile | None = File(None, description="Landmark image file")
    hint_image_file: UploadFile | None = File(
        None, description="Landmark hint image file"
    )

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    @field_validator("image_file", "hint_image_file", mode="before")
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
    photo_location_radius: int | None = Form(
        None,
        ge=1,
        le=5000,
        description="Radius in meters for taking photos from the specific photo location",
    )
    photo_latitude: float | None = Form(
        None, ge=-90, le=90, description="Latitude coordinate for photo location"
    )
    photo_longitude: float | None = Form(
        None, ge=-180, le=180, description="Longitude coordinate for photo location"
    )
    area_id: UUID | None = Form(None, description="Area ID where landmark is located")
    image_file: UploadFile | None = File(None, description="Landmark image file")
    hint_image_file: UploadFile | None = File(
        None, description="Landmark hint image file"
    )

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    @field_validator("image_file", "hint_image_file", mode="before")
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

    @field_validator(
        "latitude", "longitude", "photo_latitude", "photo_longitude", mode="before"
    )
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

    @field_validator(
        "unlock_radius_meters",
        "photo_radius_meters",
        "photo_location_radius",
        mode="before",
    )
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
    hint_image_url: str | None = Field(None, description="URL to landmark hint image")

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
    page: int = Field(1, ge=1, description="Page number (1-based)")
    page_size: int = Field(50, ge=1, le=100, description="Number of items per page")


class NearbyLandmarkResponse(TimezoneAwareSchema):
    """
    Enhanced schema for nearby landmarks response.
    Includes unlock status and area information for map display.

    Uses Pydantic v2 computed fields and validators for efficient ORM-to-schema conversion.
    """

    id: UUID = Field(..., description="Unique landmark identifier")
    unlocked: bool = Field(
        default=False, description="Whether the current user has unlocked this landmark"
    )
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    title: str = Field(..., description="Title/name of the landmark")
    description: str | None = Field(None, description="Description of the landmark")
    image: str | None = Field(None, description="URL to landmark image")
    hint_image: str | None = Field(None, description="URL to landmark hint image")
    radius: int = Field(..., description="Photo radius in meters for this landmark")
    unlock_radius: int = Field(
        ..., description="Unlock radius in meters for this landmark"
    )
    photo_location_radius: int | None = Field(
        None,
        description="Radius in meters for taking photos from the specific photo location",
    )
    photo_latitude: float | None = Field(
        None, description="Latitude coordinate for photo location"
    )
    photo_longitude: float | None = Field(
        None, description="Longitude coordinate for photo location"
    )
    badge_url: str | None = Field(
        None, description="URL to area badge associated with this landmark"
    )
    area_id: UUID = Field(..., description="Area ID where landmark is located")
    area_name: str = Field(..., description="Name of the area")
    is_area_verified: bool = Field(..., description="Whether the area is verified")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_with_status(
        cls, landmark: "Landmark", is_unlocked: bool, timezone: "ZoneInfo"
    ) -> "NearbyLandmarkResponse":
        """
        Create a NearbyLandmarkResponse from an ORM Landmark model and unlock status.

        Args:
            landmark: SQLAlchemy Landmark model with preloaded relationships
            is_unlocked: Whether the current user has unlocked this landmark
            timezone: Target timezone for datetime conversion

        Returns:
            Validated NearbyLandmarkResponse with proper timezone conversion
        """
        # Build the response dict with field mapping
        data = {
            "id": landmark.id,
            "unlocked": is_unlocked,
            "latitude": landmark.latitude,
            "longitude": landmark.longitude,
            "title": landmark.name,
            "description": landmark.description,
            "image": landmark.image_url,
            "hint_image": landmark.hint_image_url,
            "radius": landmark.photo_radius_meters,
            "unlock_radius": landmark.unlock_radius_meters,
            "photo_location_radius": landmark.photo_location_radius,
            "photo_latitude": landmark.photo_latitude,
            "photo_longitude": landmark.photo_longitude,
            "badge_url": landmark.area.badge_url,
            "area_id": landmark.area_id,
            "area_name": landmark.area.name,
            "is_area_verified": landmark.area.is_verified,
        }

        return cls.model_validate_with_timezone(data, timezone)

    @classmethod
    def from_orm_with_user(
        cls, landmark: "Landmark", user_id: UUID, timezone: "ZoneInfo"
    ) -> "NearbyLandmarkResponse":
        """
        Create a NearbyLandmarkResponse from an ORM Landmark model.

        Deprecated: Use from_orm_with_status instead.
        """
        # Check unlock status using set membership for O(1) lookup
        # Note: This requires unlocks relationship to be loaded which can be expensive
        unlocked = any(unlock.user_id == user_id for unlock in landmark.unlocks)
        return cls.from_orm_with_status(landmark, unlocked, timezone)


class NearbyLandmarksListResponse(BaseModel):
    """Schema for list of nearby landmarks with efficient batch validation and pagination."""

    landmarks: list[NearbyLandmarkResponse] = Field(
        default_factory=list, description="List of nearby landmarks"
    )
    total: int = Field(..., ge=0, description="Total number of landmarks found")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    count: int = Field(..., ge=0, description="Number of items on the current page")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_list(
        cls,
        items: list[tuple["Landmark", bool]],
        timezone: ZoneInfo,
        total: int,
        page: int,
        page_size: int,
    ) -> "NearbyLandmarksListResponse":
        """
        Create a NearbyLandmarksListResponse from a list of (Landmark, is_unlocked) tuples.

        Args:
            items: List of tuples containing (Landmark model, is_unlocked boolean)
            timezone: Target timezone for datetime conversion
            total: Total count of all landmarks (before pagination)
            page: Current page number
            page_size: Number of items per page

        Returns:
            Validated NearbyLandmarksListResponse with all landmarks converted and pagination metadata
        """
        validated_landmarks = [
            NearbyLandmarkResponse.from_orm_with_status(landmark, is_unlocked, timezone)
            for landmark, is_unlocked in items
        ]

        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

        return cls(
            landmarks=validated_landmarks,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            count=len(validated_landmarks),
        )


class NearbyLandmarksReturn(BaseReturn):
    """API response wrapper for nearby landmarks"""

    data: NearbyLandmarksListResponse | None = None
