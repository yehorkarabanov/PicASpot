from app.auth.security import get_password_hash, verify_password
from app.core.exceptions import BadRequestError, NotFoundError
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
