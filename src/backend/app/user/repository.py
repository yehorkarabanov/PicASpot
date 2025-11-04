from sqlalchemy import or_, select

from app.core.repository import BaseRepository

from .models import User


class UserRepository(BaseRepository[User]):
    """Repository for User model operations"""

    async def get_by_email_or_username(self, email: str, username: str) -> User | None:
        """Check if a user exists with the given email or username"""
        query = select(self.model).where(
            or_(self.model.email == email, self.model.username == username)
        )
        result = await self.session.execute(query)
        entity = result.scalar_one_or_none()
        return self._convert_timestamps(entity) if entity else None
