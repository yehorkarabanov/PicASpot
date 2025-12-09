import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.core.schemas import BaseReturn
from app.core.schemas_base import TimezoneAwareSchema


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserResponse(TimezoneAwareSchema):
    """User response schema with timezone-aware timestamp handling"""

    id: UUID
    username: str
    email: EmailStr
    is_superuser: bool
    is_verified: bool
    profile_picture_url: Optional[str] = None  # Presigned URL to access the image

    created_at: datetime.datetime
    updated_at: datetime.datetime


class UserUpdatePassword(BaseModel):
    password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class UserReturn(BaseReturn):
    data: UserResponse | None = None


class UserProfilePictureUrl(BaseModel):
    """Schema for returning profile picture URL"""

    url: str = Field(..., description="Presigned URL to access the profile picture")
    expires_in: int = Field(..., description="URL expiration time in seconds")


class UserProfilePictureReturn(BaseReturn):
    """Response for profile picture URL endpoint"""

    data: UserProfilePictureUrl | None = None
