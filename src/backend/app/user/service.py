import logging
from datetime import timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from app.auth.security import get_password_hash, verify_password
from app.core.exceptions import BadRequestError, NotFoundError
from app.settings import settings
from app.storage.directories import StorageDir

if TYPE_CHECKING:
    from app.storage.service import StorageService

from .repository import UserRepository
from .schemas import UserResponse, UserUpdate, UserUpdatePassword

logger = logging.getLogger(__name__)


class UserService:
    """
    Service layer for managing user operations.

    This service handles the business logic for user management, including
    retrieving, updating user information, password changes, and creating
    default users for system initialization.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        timezone: ZoneInfo | None = None,
        storage_service: "StorageService | None" = None,
    ):
        """
        Initialize the UserService.

        Args:
            user_repository: Repository instance for user data access.
            timezone: Client's timezone for datetime conversion in responses.
            storage_service: Storage service for handling profile pictures (optional).
        """
        self.user_repository = user_repository
        self.timezone = timezone or ZoneInfo("UTC")
        self.storage_service = storage_service

    async def get_user(self, user_id: str) -> UserResponse:
        """
        Retrieve a user by their ID with profile picture URL.

        Always returns a profile picture URL - either custom or default.

        Args:
            user_id: The UUID string of the user to retrieve.

        Returns:
            UserResponse: The user data with profile_picture_url.

        Raises:
            NotFoundError: If the user does not exist.
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        user_response = UserResponse.model_validate_with_timezone(user, self.timezone)

        # Always generate profile picture URL (custom or default)
        try:
            url, _ = await self.get_profile_picture_url(user_id)
            user_response.profile_picture_url = url
        except Exception as e:
            logger.warning(f"Failed to generate profile picture URL: {e}")
            # Fallback to default if something goes wrong
            user_response.profile_picture_url = settings.DEFAULT_PROFILE_PICTURE_URL

        return user_response

    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        """
        Update a user's information.

        Validates that username and email are unique before updating.

        Args:
            user_id: The UUID string of the user to update.
            user_data: The updated user data (only fields to change).

        Returns:
            UserResponse: The updated user data.

        Raises:
            NotFoundError: If the user does not exist.
            BadRequestError: If the username or email is already taken by another user.
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        update_data = user_data.model_dump(exclude_unset=True)

        # Check if username is being changed and if it's already taken
        if "username" in update_data:
            existing_user = await self.user_repository.get_by_field(
                "username", update_data["username"]
            )
            if existing_user and existing_user.id != user.id:
                raise BadRequestError(
                    f"Username '{update_data['username']}' is already taken"
                )

        # Check if email is being changed and if it's already taken
        if "email" in update_data:
            existing_user = await self.user_repository.get_by_field(
                "email", update_data["email"]
            )
            if existing_user and existing_user.id != user.id:
                raise BadRequestError(
                    f"Email '{update_data['email']}' is already taken"
                )

        for key, value in update_data.items():
            setattr(user, key, value)

        await self.user_repository.save(user)
        return UserResponse.model_validate_with_timezone(user, self.timezone)

    async def update_password(
        self, user_id: str, password_data: UserUpdatePassword
    ) -> None:
        """
        Update a user's password.

        Verifies the current password before setting the new password.

        Args:
            user_id: The UUID string of the user whose password to update.
            password_data: Contains the current password and new password.

        Raises:
            NotFoundError: If the user does not exist.
            BadRequestError: If the current password is incorrect.
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        if not verify_password(password_data.password, user.hashed_password):
            raise BadRequestError("Current password is incorrect")

        user.hashed_password = get_password_hash(password_data.new_password)
        await self.user_repository.save(user)

    async def create_default_users(self) -> None:
        """
        Create default admin and regular users from settings.

        This method is typically called during application startup to ensure
        default users exist. It checks environment variables for credentials
        and creates users if they don't already exist.

        Default users:
        - Admin user: Created with ADMIN_EMAIL and ADMIN_PASSWORD from settings.
        - Regular user: Created with USER_EMAIL and USER_PASSWORD from settings.

        Both users are created with is_verified=True for immediate access.
        """
        # Create an admin user if not exists
        if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
            existing_admin = await self.user_repository.get_by_field(
                "email", settings.ADMIN_EMAIL
            )
            if not existing_admin:
                admin_dict = {
                    "email": settings.ADMIN_EMAIL,
                    "username": settings.ADMIN_EMAIL.strip().split("@")[0],
                    "hashed_password": get_password_hash(settings.ADMIN_PASSWORD),
                    "is_verified": True,
                    "is_superuser": True,
                }
                admin_user = await self.user_repository.create(admin_dict)
                print(f"Created default admin user: {admin_user.email}")
                logger.info(f"Created default admin user: {admin_user.email}")

        # Create a regular user if not exists
        if settings.USER_EMAIL and settings.USER_PASSWORD:
            existing_user = await self.user_repository.get_by_field(
                "email", settings.USER_EMAIL
            )
            if not existing_user:
                user_dict = {
                    "email": settings.USER_EMAIL,
                    "username": settings.USER_EMAIL.strip().split("@")[0],
                    "hashed_password": get_password_hash(settings.USER_PASSWORD),
                    "is_verified": True,
                    "is_superuser": False,
                }
                regular_user = await self.user_repository.create(user_dict)
                print(f"Created default regular user: {regular_user.email}")
                logger.info(f"Created default regular user: {regular_user.email}")

    async def upload_profile_picture(
        self, user_id: str, image_data: bytes, filename: str, content_type: str
    ) -> str:
        """
        Upload a user's profile picture.

        Args:
            user_id: The UUID string of the user.
            image_data: The image file data as bytes.
            filename: Original filename.
            content_type: MIME type of the image.

        Returns:
            str: The storage path of the uploaded image.

        Raises:
            NotFoundError: If the user does not exist.
            BadRequestError: If storage service is not available.
        """
        if not self.storage_service:
            raise BadRequestError("Storage service not configured")

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Delete old profile picture if exists
        if user.profile_picture_path:
            try:
                await self.storage_service.remove_object(user.profile_picture_path)
            except Exception as e:
                logger.warning(f"Failed to delete old profile picture: {e}")

        # Upload new profile picture to users directory
        result = await self.storage_service.upload_file(
            file_data=image_data,
            original_filename=filename,
            path_prefix=StorageDir.USERS,
            content_type=content_type,
        )

        # Update user record with new profile picture path
        user.profile_picture_path = result["object_path"]
        await self.user_repository.save(user)

        logger.info(f"User {user_id} uploaded profile picture: {result['object_path']}")
        return result["object_path"]

    async def get_profile_picture_url(
        self, user_id: str, expires: timedelta | None = None
    ) -> tuple[str, int]:
        """
        Get a presigned URL for a user's profile picture.

        If the user has no custom profile picture, returns the default picture URL.

        Args:
            user_id: The UUID string of the user.
            expires: Optional custom expiration time for the URL.

        Returns:
            tuple[str, int]: (presigned_url or default_url, expiration_seconds)

        Raises:
            NotFoundError: If the user does not exist.
            BadRequestError: If storage service is not available for custom pictures.
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Return default profile picture URL if user has no custom picture
        if not user.profile_picture_path:
            return (
                settings.DEFAULT_PROFILE_PICTURE_URL,
                0,
            )  # 0 means never expires (static file)

        # User has custom profile picture - generate presigned URL
        if not self.storage_service:
            raise BadRequestError("Storage service not configured")

        # Generate presigned URL
        url = await self.storage_service.get_image_url(
            user.profile_picture_path, expires=expires
        )

        # Get expiration seconds
        expiration_seconds = int(
            (expires or self.storage_service.default_url_expiry).total_seconds()
        )

        return url, expiration_seconds

    async def delete_profile_picture(self, user_id: str) -> None:
        """
        Delete a user's profile picture.

        Args:
            user_id: The UUID string of the user.

        Raises:
            NotFoundError: If the user does not exist or has no profile picture.
            BadRequestError: If storage service is not available.
        """
        if not self.storage_service:
            raise BadRequestError("Storage service not configured")

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        if not user.profile_picture_path:
            raise NotFoundError("User has no profile picture")

        # Delete from storage
        await self.storage_service.remove_object(user.profile_picture_path)

        # Update user record
        user.profile_picture_path = None
        await self.user_repository.save(user)

        logger.info(f"User {user_id} deleted profile picture")
