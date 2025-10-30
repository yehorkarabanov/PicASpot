import logging

from app.auth.security import get_password_hash, verify_password
from app.core.exceptions import BadRequestError, NotFoundError
from app.settings import settings

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

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the UserService.

        Args:
            user_repository: Repository instance for user data access.
        """
        self.user_repository = user_repository

    async def get_user(self, user_id: str) -> UserResponse:
        """
        Retrieve a user by their ID.

        Args:
            user_id: The UUID string of the user to retrieve.

        Returns:
            UserResponse: The user data.

        Raises:
            NotFoundError: If the user does not exist.
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return UserResponse.model_validate(user)

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
        return UserResponse.model_validate(user)

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
