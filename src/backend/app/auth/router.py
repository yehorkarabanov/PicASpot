from fastapi import APIRouter, Form

from app.auth.dependencies import AuthServiceDep
from app.auth.schemas import (
    AuthReturn,
    EmailRequest,
    Token,
    UserCreate,
    UserLogin,
    UserLoginResponse,
    UserLoginReturn,
    AccessToken,
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
    "/resend-verification-token",
    response_model=AuthReturn,
    response_model_exclude_none=True,
)
async def resend_verification_token(
    email_request: EmailRequest,
    auth_service: AuthServiceDep,
) -> AuthReturn:
    """Resend verification email to the user."""
    await auth_service.resend_verification_token(email_request.email)
    return AuthReturn(message="Verification email resent successfully.")


@router.post("/login", response_model=UserLoginReturn, response_model_exclude_none=True)
async def login(login_data: UserLogin, auth_service: AuthServiceDep) -> UserLoginReturn:
    """Login a user and return an access token."""
    data = await auth_service.login(login_data)
    return UserLoginReturn(data=data, message="Login successful.")


@router.post(
    "/access-token", response_model=AccessToken, response_model_exclude_none=True
)
async def get_access_token(
    auth_service: AuthServiceDep,
    username: str = Form(...),
    password: str = Form(...),
) -> AccessToken:
    """Get access token using form data."""
    login_data = UserLogin(username=username, password=password)
    user_login_response: UserLoginResponse = await auth_service.login(login_data)
    return user_login_response.token


@router.post("/verify", response_model=AuthReturn, response_model_exclude_none=True)
async def verify_token(token: Token, auth_service: AuthServiceDep):
    """Verify email using the provided token."""
    await auth_service.verify_token(token.token)
    return AuthReturn(message="Email verified successfully.")