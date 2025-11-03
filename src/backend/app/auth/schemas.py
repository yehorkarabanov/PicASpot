import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.schemas import BaseReturn
from app.user.schemas import UserBase, UserResponse


class UserCreate(UserBase):
    # Password must be at least 8 characters, contain at least one uppercase letter and one number
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not re.match(r"^(?=.*[A-Z])(?=.*\d).{8,}$", v):
            raise ValueError(
                "Password must be at least 8 characters, contain at least one uppercase letter and one number"
            )
        return v


class UserLogin(BaseModel):
    username: str
    password: str = Field(min_length=8)


class Token(BaseModel):
    token: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserLoginResponse(UserResponse):
    token: AccessToken


class UserLoginReturn(BaseReturn):
    data: UserLoginResponse | None = None


class EmailRequest(BaseModel):
    email: EmailStr


class AuthReturn(BaseReturn):
    data: UserResponse | None = None


class UserResetPassword(BaseModel):
    password: str = Field(..., min_length=8)
    token: str
