from fastapi import APIRouter

from app.auth.dependencies import AuthServiceDep
from app.auth.schemas import (
    AuthReturn,
    EmailRequest,
    Token,
    UserCreate,
    UserLogin,
    UserLoginResponse,
)

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/register", response_model=AuthReturn, response_model_exclude_none=True)
async def register(
    user_data: UserCreate,
    auth_service: AuthServiceDep,
) -> AuthReturn:
    """Register a new user."""
    await auth_service.register(user_data)
    return AuthReturn(message="User registered successfully. Please verify your email.")


@router.post(
    "/resend-verification-email",
    response_model=AuthReturn,
    response_model_exclude_none=True,
)
async def resend_verification_email(
    email_request: EmailRequest,
    auth_service: AuthServiceDep,
) -> AuthReturn:
    """Resend verification email to the user."""
    await auth_service.resend_verification_email(email_request.email)
    return AuthReturn(message="Verification email resent successfully.")


@router.post("/login", response_model=UserLoginResponse, response_model_exclude_none=True)
async def login(
    user_data: UserLogin,
    auth_service: AuthServiceDep,
) -> Token:
    """Login a user and return an access token."""
    return await auth_service.login(user_data)
