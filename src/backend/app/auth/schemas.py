from pydantic import BaseModel, Field, ConfigDict

from app.core.schemas import BaseReturn


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    password2: str


class UserLogin(UserBase):
    password: str
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "stringst",
            }
        },
    )


class UserResponse(UserBase):
    id: str
    is_superuser: bool
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    token: str


class EmailRequest(BaseModel):
    email: str


class AuthReturn(BaseReturn):
    data: UserResponse | None = None
