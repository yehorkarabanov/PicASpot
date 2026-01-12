from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.schemas import BaseReturn
from app.core.schemas_base import TimezoneAwareSchema
from app.landmark.schemas import NearbyLandmarksListResponse

if TYPE_CHECKING:
    from .models import Area


class AreaBase(BaseModel):
    """Base schema with common area attributes"""

    name: str = Field(..., min_length=1, max_length=255, description="Area name")
    description: str | None = Field(
        None, max_length=1000, description="Area description"
    )


class AreaCreate(BaseModel):
    """Schema for creating a new area with multipart form data support"""

    name: str = Form(..., min_length=1, max_length=255, description="Area name")
    description: str | None = Form(
        None, max_length=1000, description="Area description"
    )
    image_file: UploadFile | None = File(None, description="Area image file")
    badge_file: UploadFile | None = File(None, description="Area badge file")
    parent_area_id: UUID | None = Form(
        None, description="Parent area ID for hierarchical structure"
    )

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    @field_validator("image_file", "badge_file", mode="before")
    @classmethod
    def validate_file_fields(cls, v):
        """Convert empty string to None for file upload fields"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

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
        raise ValueError(
            f"parent_area_id must be a valid UUID or None, got {type(v).__name__}"
        )

    @field_validator("name", "description", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        """Convert empty string to None for string fields"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class AreaUpdate(BaseModel):
    """Schema for updating an existing area with multipart form data support - all fields optional"""

    name: str | None = Form(None, min_length=1, max_length=255, description="Area name")
    description: str | None = Form(
        None, max_length=1000, description="Area description"
    )
    image_file: UploadFile | None = File(None, description="Area image file")
    badge_file: UploadFile | None = File(None, description="Area badge file")
    parent_area_id: UUID | None = Form(None, description="Parent area ID")

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    @field_validator("image_file", "badge_file", mode="before")
    @classmethod
    def validate_file_fields(cls, v):
        """Convert empty string to None for file upload fields"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

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
        raise ValueError(
            f"parent_area_id must be a valid UUID or None, got {type(v).__name__}"
        )

    @field_validator("name", "description", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        """Convert empty strings to None for optional fields"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class AreaResponse(AreaBase, TimezoneAwareSchema):
    """Schema for area responses - includes all read-only fields with timezone-aware timestamps"""

    id: UUID = Field(..., description="Unique area identifier")
    parent_area_id: UUID | None = Field(None, description="Parent area ID")
    is_verified: bool = Field(False, description="Whether area is verified")
    image_url: str | None = Field(None, description="URL to area image")
    badge_url: str | None = Field(None, description="URL to area badge")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


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


class AreaLandmarksResponse(BaseModel):
    """Schema for area details with its landmarks"""

    area: AreaResponse = Field(..., description="Area details")
    landmarks: NearbyLandmarksListResponse = Field(
        ..., description="List of landmarks in the area"
    )


class AreaLandmarksReturn(BaseReturn):
    """API response wrapper for area landmarks"""

    data: AreaLandmarksResponse | None = None


class AreaNearbyRequest(BaseModel):
    """Schema for finding nearby areas based on landmark proximity"""

    latitude: float = Field(..., ge=-90, le=90, description="Current latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Current longitude")
    radius_meters: int = Field(
        1000, ge=1, le=50000, description="Search radius in meters"
    )
    only_verified: bool = Field(default=False, description="Only return verified areas")
    require_all_landmarks_in_radius: bool = Field(
        False,
        description="Only return areas where all landmarks are within the search radius",
    )
    page: int = Field(1, ge=1, description="Page number (1-based)")
    page_size: int = Field(50, ge=1, le=100, description="Number of items per page")


class NearbyAreaResponse(AreaResponse):
    """Schema for nearby area responses with landmark count within radius"""

    landmark_count_in_radius: int = Field(
        ...,
        ge=0,
        description="Number of landmarks in this area within the search radius",
    )


class NearbyAreasListResponse(BaseModel):
    """Schema for list of nearby areas with pagination."""

    areas: list[NearbyAreaResponse] = Field(
        default_factory=list, description="List of nearby areas"
    )
    total: int = Field(..., ge=0, description="Total number of areas found")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    count: int = Field(..., ge=0, description="Number of items on the current page")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_list(
        cls,
        items: list[tuple["Area", int]],
        timezone: ZoneInfo,
        total: int,
        page: int,
        page_size: int,
    ) -> "NearbyAreasListResponse":
        """
        Create a NearbyAreasListResponse from a list of (Area, landmark_count) tuples.

        Args:
            items: List of tuples containing (Area model, landmark_count int)
            timezone: Target timezone for datetime conversion
            total: Total count of all areas (before pagination)
            page: Current page number
            page_size: Number of items per page

        Returns:
            Validated NearbyAreasListResponse with all areas converted and pagination metadata
        """
        validated_areas = [
            NearbyAreaResponse(
                **AreaResponse.model_validate_with_timezone(
                    area, timezone
                ).model_dump(),
                landmark_count_in_radius=count,
            )
            for area, count in items
        ]

        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

        return cls(
            areas=validated_areas,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            count=len(validated_areas),
        )


class NearbyAreasReturn(BaseReturn):
    """API response wrapper for nearby areas"""

    data: NearbyAreasListResponse | None = None
