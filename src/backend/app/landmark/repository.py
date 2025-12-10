import uuid

from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_SetSRID
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

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
    ) -> list[Landmark]:
        """
        Get landmarks within a given radius from a point.

        Args:
            latitude: Latitude of the center point
            longitude: Longitude of the center point
            radius_meters: Search radius in meters
            user_id: Current user ID to check unlock status
            area_id: Optional area ID to filter landmarks
            only_verified: If True, only return landmarks from verified areas
            load_from_same_area: If True, load all landmarks from areas found within radius

        Returns:
            List of landmarks with their relationships loaded
        """
        # Create a point from the given coordinates
        user_point = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)

        # Base query with necessary joins
        query = (
            select(Landmark)
            .join(Area, Landmark.area_id == Area.id)
            .outerjoin(
                Unlock,
                (Unlock.landmark_id == Landmark.id) & (Unlock.user_id == user_id),
            )
            .options(
                joinedload(Landmark.area),
                joinedload(Landmark.creator),
                selectinload(Landmark.unlocks).joinedload(Unlock.user),
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

        # Execute the query to get landmarks within radius
        result = await self.session.execute(query)
        landmarks = list(result.scalars().unique().all())

        # If load_from_same_area is True, load all landmarks from the same areas
        if load_from_same_area and landmarks:
            area_ids = list({landmark.area_id for landmark in landmarks})

            # Query all landmarks from these areas
            area_query = (
                select(Landmark)
                .join(Area, Landmark.area_id == Area.id)
                .outerjoin(
                    Unlock,
                    (Unlock.landmark_id == Landmark.id) & (Unlock.user_id == user_id),
                )
                .where(Landmark.area_id.in_(area_ids))
                .options(
                    joinedload(Landmark.area),
                    joinedload(Landmark.creator),
                    selectinload(Landmark.unlocks).joinedload(Unlock.user),
                )
            )

            if only_verified:
                area_query = area_query.where(Area.is_verified == True)  # noqa: E712

            area_result = await self.session.execute(area_query)
            landmarks = list(area_result.scalars().unique().all())

        return landmarks
