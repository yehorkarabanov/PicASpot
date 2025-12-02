"""
User model factory for test data generation.

This factory creates User model instances with realistic fake data
for testing purposes.
"""

import uuid

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import get_password_hash
from app.user.models import User

fake = Faker()


class UserFactory:
    """
    Factory for creating User instances in tests.

    This class provides methods to create users with various configurations
    (verified, unverified, superuser, etc.) using realistic fake data.
    """

    @staticmethod
    async def create(
        session: AsyncSession,
        username: str | None = None,
        email: str | None = None,
        password: str = "testpassword123",
        is_verified: bool = True,
        is_superuser: bool = False,
        **kwargs,
    ) -> User:
        """
        Create a user with the given attributes.

        Args:
            session: Database session
            username: Username (auto-generated if None)
            email: Email address (auto-generated if None)
            password: Plain text password (will be hashed)
            is_verified: Email verification status
            is_superuser: Superuser/admin status
            **kwargs: Additional user attributes

        Returns:
            Created User instance

        Example:
            user = await UserFactory.create(session)
            admin = await UserFactory.create(session, is_superuser=True)
            unverified = await UserFactory.create(session, is_verified=False)
        """
        user_data = {
            "id": uuid.uuid4(),
            "username": username or fake.user_name(),
            "email": email or fake.email(),
            "hashed_password": get_password_hash(password),
            "is_verified": is_verified,
            "is_superuser": is_superuser,
        }
        user_data.update(kwargs)

        user = User(**user_data)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def create_batch(
        session: AsyncSession,
        count: int = 5,
        **kwargs,
    ) -> list[User]:
        """
        Create multiple users at once.

        Args:
            session: Database session
            count: Number of users to create
            **kwargs: Common attributes for all users

        Returns:
            List of created User instances

        Example:
            users = await UserFactory.create_batch(session, count=10)
        """
        users = []
        for _ in range(count):
            user = await UserFactory.create(session, **kwargs)
            users.append(user)
        return users

    @staticmethod
    async def create_verified_user(
        session: AsyncSession,
        **kwargs,
    ) -> User:
        """
        Create a verified regular user.

        This is the most common type of user for testing.
        """
        return await UserFactory.create(
            session,
            is_verified=True,
            is_superuser=False,
            **kwargs,
        )

    @staticmethod
    async def create_unverified_user(
        session: AsyncSession,
        **kwargs,
    ) -> User:
        """
        Create an unverified user.

        Useful for testing email verification flows.
        """
        return await UserFactory.create(
            session,
            is_verified=False,
            is_superuser=False,
            **kwargs,
        )

    @staticmethod
    async def create_superuser(
        session: AsyncSession,
        **kwargs,
    ) -> User:
        """
        Create a superuser/admin.

        Useful for testing admin-only functionality.
        """
        return await UserFactory.create(
            session,
            is_verified=True,
            is_superuser=True,
            username=kwargs.get("username", f"admin_{fake.user_name()}"),
            **kwargs,
        )

    @staticmethod
    def generate_username() -> str:
        """Generate a random username."""
        return fake.user_name()

    @staticmethod
    def generate_email() -> str:
        """Generate a random email address."""
        return fake.email()

    @staticmethod
    def generate_password() -> str:
        """Generate a random password."""
        return fake.password(length=12)


__all__ = ["UserFactory"]
