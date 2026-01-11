import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, selectinload

from app.core.repository import BaseRepository
from app.landmark.models import Landmark
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

    async def get_unlock_with_relations(
        self,
        unlock_id: uuid.UUID,
        user_id: uuid.UUID,
        load_attempt: bool = True,
        load_landmark: bool = True,
        load_area: bool = True,
    ) -> Unlock | None:
        """
        Get an unlock with optional eager loading of related entities.

        Args:
            unlock_id: The unlock ID.
            user_id: The user ID (for ownership verification).
            load_attempt: Whether to load the attempt relation.
            load_landmark: Whether to load the landmark relation.
            load_area: Whether to load the area relation (requires load_landmark=True).

        Returns:
            The unlock with loaded relations, or None if not found.
        """
        stmt = select(Unlock).where(
            Unlock.id == unlock_id,
            Unlock.user_id == user_id,
        )

        load_options: list[Any] = []
        # Use joinedload for single-entity relations (attempt is 1:1)
        if load_attempt:
            load_options.append(joinedload(Unlock.attempt))
        if load_landmark:
            if load_area:
                load_options.append(
                    joinedload(Unlock.landmark).selectinload(Landmark.area)
                )
            else:
                load_options.append(joinedload(Unlock.landmark))

        if load_options:
            stmt = stmt.options(*load_options)

        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_user_unlocks_paginated(
        self,
        user_id: uuid.UUID,
        limit: int,
        offset: int,
        load_attempt: bool = True,
        load_landmark: bool = True,
        load_area: bool = True,
    ) -> tuple[list[Unlock], int]:
        """
        Get paginated unlocks for a user with optional eager loading.

        Args:
            user_id: The user ID.
            limit: Maximum number of results.
            offset: Number of results to skip.
            load_attempt: Whether to load the attempt relation.
            load_landmark: Whether to load the landmark relation.
            load_area: Whether to load the area relation (requires load_landmark=True).

        Returns:
            Tuple of (list of unlocks, total count).
        """
        # Build base query with filters
        base_filter = Unlock.user_id == user_id

        # Count query (efficient - no joins needed)
        count_stmt = select(func.count()).select_from(Unlock).where(base_filter)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Early return if no results
        if total == 0:
            return [], 0

        # Main query with eager loading
        stmt = (
            select(Unlock)
            .where(base_filter)
            .order_by(Unlock.unlocked_at.desc())
            .limit(limit)
            .offset(offset)
        )

        load_options: list[Any] = []
        # Use selectinload for collections/chained relations (better for pagination)
        if load_attempt:
            load_options.append(selectinload(Unlock.attempt))
        if load_landmark:
            if load_area:
                load_options.append(
                    selectinload(Unlock.landmark).selectinload(Landmark.area)
                )
            else:
                load_options.append(selectinload(Unlock.landmark))

        if load_options:
            stmt = stmt.options(*load_options)

        result = await self.session.execute(stmt)
        unlocks = list(result.scalars().all())

        return unlocks, total


class AttemptRepository(BaseRepository[Attempt]):
    """Repository for Attempt model operations"""
