import uuid

from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_SetSRID
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.area.models import Area
from app.core.repository import BaseRepository
from app.unlock.models import Unlock

from .models import Landmark


class LandmarkRepository(BaseRepository[Landmark]):
    """Repository for Landmark model operations"""

    async def get_nearby_landmarks(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int,
        user_id: uuid.UUID,
        area_id: uuid.UUID | None = None,
        only_verified: bool = False,
        load_from_same_area: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[tuple[Landmark, bool]], int]:
        """
        Get landmarks within a given radius from a point with pagination.

        Args:
            latitude: Latitude of the center point
            longitude: Longitude of the center point
            radius_meters: Search radius in meters
            user_id: Current user ID to check unlock status
            area_id: Optional area ID to filter landmarks
            only_verified: If True, only return landmarks from verified areas
            load_from_same_area: If True, load all landmarks from areas found within radius
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            Tuple of (list of (landmark, is_unlocked) tuples, total count)
        """
        # Create a point from the given coordinates
        user_point = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)

        # Base query with necessary joins
        # Select Landmark and a boolean indicating if the user has unlocked it
        query = (
            select(Landmark, Unlock.user_id.is_not(None).label("is_unlocked"))
            .join(Area, Landmark.area_id == Area.id)
            .outerjoin(
                Unlock,
                (Unlock.landmark_id == Landmark.id) & (Unlock.user_id == user_id),
            )
            .options(
                joinedload(Landmark.area),
                # Removed joinedload(Landmark.creator) as it's not used in response
                # Removed selectinload(Landmark.unlocks) to avoid N+1 query for all unlocks
            )
        )

        # Filter by distance
        query = query.where(
            ST_DWithin(
                Landmark.location,
                user_point,
                radius_meters,
                True,  # Use spheroid for accurate distance calculation
            )
        )

        # Filter by area if specified
        if area_id is not None:
            query = query.where(Landmark.area_id == area_id)

        # Filter by verified areas if specified
        if only_verified:
            query = query.where(Area.is_verified == True)  # noqa: E712

        # If load_from_same_area is True, load all landmarks from the same areas
        area_ids_subquery = None
        if load_from_same_area:
            # Subquery to get area_ids from landmarks within radius
            area_ids_subquery = (
                select(Landmark.area_id)
                .join(Area, Landmark.area_id == Area.id)
                .where(
                    ST_DWithin(
                        Landmark.location,
                        user_point,
                        radius_meters,
                        True,
                    )
                )
            )

            if area_id is not None:
                area_ids_subquery = area_ids_subquery.where(Landmark.area_id == area_id)

            if only_verified:
                area_ids_subquery = area_ids_subquery.where(Area.is_verified == True)  # noqa: E712

            # Replace query to get all landmarks from these areas
            query = (
                select(Landmark, Unlock.user_id.is_not(None).label("is_unlocked"))
                .join(Area, Landmark.area_id == Area.id)
                .outerjoin(
                    Unlock,
                    (Unlock.landmark_id == Landmark.id) & (Unlock.user_id == user_id),
                )
                .where(Landmark.area_id.in_(area_ids_subquery))
                .options(
                    joinedload(Landmark.area),
                )
            )

            if only_verified:
                query = query.where(Area.is_verified == True)  # noqa: E712

        # Count query - create a count query without joins that are only for loading relationships
        # Optimize: Only join Area if we need to filter by verified status
        if only_verified:
            count_query = select(func.count(Landmark.id)).join(
                Area, Landmark.area_id == Area.id
            )
        else:
            count_query = select(func.count(Landmark.id))

        # Apply the same filters as the main query
        if load_from_same_area and area_ids_subquery is not None:
            count_query = count_query.where(Landmark.area_id.in_(area_ids_subquery))
        else:
            count_query = count_query.where(
                ST_DWithin(
                    Landmark.location,
                    user_point,
                    radius_meters,
                    True,
                )
            )
            if area_id is not None:
                count_query = count_query.where(Landmark.area_id == area_id)

        if only_verified:
            count_query = count_query.where(Area.is_verified == True)  # noqa: E712

        # Execute count query
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar_one()

        # Apply pagination to main query
        query = query.limit(limit).offset(offset)

        # Execute the main query to get landmarks
        result = await self.session.execute(query)
        # Result contains tuples of (Landmark, is_unlocked)
        landmarks_with_status = list(result.all())

        return landmarks_with_status, total_count
