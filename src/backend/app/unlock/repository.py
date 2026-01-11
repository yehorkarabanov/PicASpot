import uuid

from sqlalchemy import select

from app.core.repository import BaseRepository
from app.unlock.models import Attempt, Unlock


class UnlockRepository(BaseRepository[Unlock]):
    """Repository for Unlock model operations"""

    async def get_by_user_and_landmark(
        self, user_id: uuid.UUID, landmark_id: uuid.UUID
    ) -> Unlock | None:
        """
        Get an unlock by user and landmark.

        Args:
            user_id: The user ID.
            landmark_id: The landmark ID.

        Returns:
            The unlock if found, None otherwise.
        """
        stmt = select(Unlock).where(
            Unlock.user_id == user_id,
            Unlock.landmark_id == landmark_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class AttemptRepository(BaseRepository[Attempt]):
    """Repository for Attempt model operations"""
