from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    is_superuser: bool
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)


class UserUpdatePassword(BaseModel):
    password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class StudentData(BaseModel):
    id: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)