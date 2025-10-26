from app.auth.security import get_password_hash, verify_password
from app.core.exceptions import BadRequestError, NotFoundError
from app.settings import settings
from app.user.repository import UserRepository
from app.user.schemas import UserResponse, UserUpdate, UserUpdatePassword


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_user(self, user_id: str) -> UserResponse:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return UserResponse.model_validate(user)

    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
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
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        if not verify_password(password_data.password, user.hashed_password):
            raise BadRequestError("Current password is incorrect")

        user.hashed_password = get_password_hash(password_data.new_password)
        await self.user_repository.save(user)

    async def create_default_users(self):
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
