import datetime
from uuid import UUID

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, ConfigDict, Field

from app.area.schemas import AreaResponse
from app.core.schemas import BaseReturn
from app.core.schemas_base import TimezoneAwareSchema
from app.landmark.schemas import LandmarkResponse


class UnlockCreate(BaseModel):
    """Schema for creating a new unlock (verifying a photo)"""

    landmark_id: UUID = Form(..., description="Landmark ID to verify")
    image_file: UploadFile = File(..., description="Photo of the landmark")

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)


class UnlockRequestParams(BaseModel):
    """Schema for unlock request query parameters"""

    load_attempt_data: bool = Field(
        default=True, description="If true, include attempt details in the response"
    )
    load_landmark_data: bool = Field(
        default=True, description="If true, include landmark details in the response"
    )
    load_area_data: bool = Field(
        default=True,
        description="If true, include area-related data for the landmark, load_landmark_data must be true",
    )

    model_config = ConfigDict(extra="forbid")


class UnlockListRequestParams(UnlockRequestParams):
    """Schema for unlock list request query parameters"""

    page: int = Field(default=1, ge=1, description="Page number for pagination")
    page_size: int = Field(
        default=10, ge=1, le=100, description="Number of unlocks per page"
    )

    model_config = ConfigDict(extra="forbid")


class AttemptResponse(TimezoneAwareSchema):
    """Schema for attempt response"""

    id: UUID
    landmark_id: UUID
    status: str
    photo_url: str
    similarity_score: float | None
    error_message: str | None
    landmark: LandmarkResponse | None = None
    area: AreaResponse | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(extra="forbid", from_attributes=True)


class AttemptRequestParams(BaseModel):
    """Schema for attempt request query parameters"""

    load_landmark_data: bool = Field(
        default=False, description="If true, include landmark details in the response"
    )
    load_area_data: bool = Field(
        default=False,
        description="If true, include area-related data for the landmark, load_landmark_data must be true",
    )

    model_config = ConfigDict(extra="forbid")


class AttemptListRequestParams(AttemptRequestParams):
    """Schema for attempt list request query parameters"""

    page: int = Field(default=1, ge=1, description="Page number for pagination")
    page_size: int = Field(
        default=10, ge=1, le=100, description="Number of attempts per page"
    )

    model_config = ConfigDict(extra="forbid")


class AttemptReturn(BaseReturn):
    """Schema for attempt return response"""

    data: AttemptResponse

    model_config = ConfigDict(extra="forbid")


class AttemptListResponse(BaseModel):
    """Schema for a list of attempt responses"""

    attempts: list[AttemptResponse] = Field(
        default_factory=list, description="List of attempts"
    )
    total: int = Field(..., ge=0, description="Total number of attempts")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Page size")
    total_pages: int = Field(..., ge=1, description="Total number of pages")
    count: int = Field(..., ge=0, description="Number of attempts in the current page")

    model_config = ConfigDict(extra="forbid")


class AttemptListReturn(BaseReturn):
    """Schema for attempt list return response"""

    data: AttemptListResponse

    model_config = ConfigDict(extra="forbid")


class UnlockResponse(TimezoneAwareSchema):
    """Schema for unlock response"""

    id: UUID
    user_id: UUID
    landmark_id: UUID
    attempt_id: UUID
    area: AreaResponse | None
    landmark: LandmarkResponse | None
    attempt: AttemptResponse | None
    photo_url: str
    is_posted_to_feed: bool
    unlocked_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(extra="forbid", from_attributes=True)


class UnlockReturn(BaseReturn):
    """Schema for unlock return response"""

    data: UnlockResponse

    model_config = ConfigDict(extra="forbid")


class UnlockListResponse(BaseModel):
    """Schema for a list of unlock responses"""

    unlocks: list[UnlockResponse] = Field(
        default_factory=list, description="List of unlocks"
    )
    total: int = Field(..., ge=0, description="Total number of unlocks")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Page size")
    total_pages: int = Field(..., ge=1, description="Total number of pages")
    count: int = Field(..., ge=0, description="Number of unlocks in the current page")

    model_config = ConfigDict(extra="forbid")


class UnlockListReturn(BaseReturn):
    """Schema for unlock list return response"""

    data: UnlockListResponse

    model_config = ConfigDict(extra="forbid")
