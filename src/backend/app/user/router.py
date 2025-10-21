from fastapi import APIRouter

from app.auth.dependencies import CurrentUserDep
from app.core.schemas import BaseReturn
from app.user.schemas import UserReturn, UserUpdate, UserUpdatePassword

from .dependencies import UserServiceDep

router = APIRouter(tags=["users"], prefix="/users")


@router.get("/me", response_model=UserReturn, response_model_exclude_none=True)
async def get_current_user(
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
) -> UserReturn:
    """Get the current user's profile."""
    user_response = await user_service.get_user(current_user.id)
    return UserReturn(message="User retrieved successfully", data=user_response)


@router.patch("/me", response_model=UserReturn, response_model_exclude_none=True)
async def update_current_user(
    user_data: UserUpdate,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
) -> UserReturn:
    """Update the current user's profile."""
    user_response = await user_service.update_user(str(current_user.id), user_data)
    return UserReturn(message="User updated successfully", data=user_response)


@router.put("/me/password", response_model=UserReturn, response_model_exclude_none=True)
async def update_current_user_password(
    password_data: UserUpdatePassword,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
) -> BaseReturn:
    """Update the current user's password."""
    await user_service.update_password(str(current_user.id), password_data)
    return BaseReturn(message="Password updated successfully")
