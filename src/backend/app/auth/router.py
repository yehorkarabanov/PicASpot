from fastapi import APIRouter, Depends

from app.auth.dependencies import get_auth_service
from app.auth.schemas import UserCreate, AuthReturn
from app.auth.service import AuthService

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/register", response_model=AuthReturn, response_model_exclude_none=True)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthReturn:
    """Register a new user."""
    await auth_service.register(user_data)
    return AuthReturn(message="User registered successfully. Please verify your email.")