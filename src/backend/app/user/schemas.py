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



class UserUpdatePassword(BaseModel):
    password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class UserReturn(BaseReturn):
    data: UserResponse | None = None
