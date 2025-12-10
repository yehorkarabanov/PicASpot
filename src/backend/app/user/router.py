from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.auth.dependencies import CurrentUserDep
from app.core.schemas import BaseReturn
from app.settings import settings

from .dependencies import UserServiceDep
from .schemas import (
    UserProfilePictureReturn,
    UserProfilePictureUrl,
    UserReturn,
    UserUpdate,
    UserUpdatePassword,
)

router = APIRouter(tags=["user"], prefix="/user")


@router.get("/me", response_model=UserReturn, response_model_exclude_none=True)
async def get_current_user(
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
) -> UserReturn:
    """Get the current user's profile."""
    user_response = await user_service.get_user(str(current_user.id))
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


@router.get(
    "/me/profile-picture",
    response_model=UserProfilePictureReturn,
    response_model_exclude_none=True,
)
async def get_profile_picture_url(
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
) -> UserProfilePictureReturn:
    """
    Get a presigned URL for the current user's profile picture.

    Returns a temporary URL that can be used to access the profile picture directly.
    The URL expires after a set time (default: 1 hour).
    """
    url, expires_in = await user_service.get_profile_picture_url(str(current_user.id))

    return UserProfilePictureReturn(
        message="Profile picture URL generated successfully",
        data=UserProfilePictureUrl(url=url, expires_in=expires_in),
    )


@router.post(
    "/me/profile-picture",
    response_model=UserProfilePictureReturn,
    response_model_exclude_none=True,
)
async def upload_profile_picture(
    file: UploadFile = File(...),
    user_service: UserServiceDep = None,
    current_user: CurrentUserDep = None,
) -> UserProfilePictureReturn:
    """
    Upload a profile picture for the current user.

    Accepts image files (JPEG, PNG, WEBP).
    Replaces any existing profile picture.
    """
    # Validate file type
    if file.content_type not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_MIME_TYPES)}",
        )

    # Validate file size
    file_data = await file.read()
    file_size_mb = len(file_data) / (1024 * 1024)

    if file_size_mb > settings.MAX_PROFILE_PICTURE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_PROFILE_PICTURE_SIZE_MB}MB",
        )

    # Upload the file
    await user_service.upload_profile_picture(
        user_id=str(current_user.id),
        image_data=file_data,
        filename=file.filename,
        content_type=file.content_type,
    )

    # Generate URL for the newly uploaded picture
    url, expires_in = await user_service.get_profile_picture_url(str(current_user.id))

    return UserProfilePictureReturn(
        message="Profile picture uploaded successfully",
        data=UserProfilePictureUrl(url=url, expires_in=expires_in),
    )


@router.delete("/me/profile-picture", response_model=BaseReturn)
async def delete_profile_picture(
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
) -> BaseReturn:
    """Delete the current user's profile picture."""
    await user_service.delete_profile_picture(str(current_user.id))
    return BaseReturn(message="Profile picture deleted successfully")


@router.put("/me/password", response_model=UserReturn, response_model_exclude_none=True)
async def update_current_user_password(
    password_data: UserUpdatePassword,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
) -> BaseReturn:
    """Update the current user's password."""
    await user_service.update_password(str(current_user.id), password_data)
    return BaseReturn(message="Password updated successfully")
