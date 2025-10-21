from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.schemas import BaseReturn


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    # Password must be at least 8 characters, contain at least one uppercase letter and one number
    password: str = Field(min_length=8)

    # @field_validator('password')
    # @classmethod
    # def validate_password(cls, v):
    #     if not re.match(r'^(?=.*[A-Z])(?=.*\d).{8,}$', v):
    #         raise ValueError('Password must be at least 8 characters, contain at least one uppercase letter and one number')
    #     return v


class UserLogin(BaseModel):
    username: str
    password: str = Field(min_length=8)


class UserResponse(UserBase):
    id: str
    is_superuser: bool
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    token: str


class UserLoginResponse(UserResponse, Token):
    pass


class EmailRequest(BaseModel):
    email: EmailStr


class AuthReturn(BaseReturn):
    data: UserResponse | None = None
