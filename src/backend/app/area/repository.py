import uuid

from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_SetSRID
from sqlalchemy import exists, func, literal_column, select
from sqlalchemy.orm import aliased

from app.core.repository import BaseRepository
from app.landmark.models import Landmark

from .models import Area


class AreaRepository(BaseRepository[Area]):
    """Repository for Area model operations"""

    async def check_circular_reference(
        self, area_id: uuid.UUID, parent_area_id: uuid.UUID, max_depth: int = 10
    ) -> tuple[bool, bool]:
        """
        Check if setting a parent would create a circular reference.

        Uses PostgreSQL recursive CTE to efficiently traverse the parent chain
        in a single query instead of multiple round trips.

        Args:
            area_id: The UUID of the area being updated.
            parent_area_id: The UUID of the proposed parent area.
            max_depth: Maximum depth to traverse (safety limit).

        Returns:
            Tuple of (has_cycle, hit_depth_limit):
                - has_cycle: True if a circular reference would be created.
                - hit_depth_limit: True if we hit max_depth without reaching the top.
        """
        # Define the recursive CTE for traversing parent chain
        parent_chain_cte = (
            select(
                Area.id,
                Area.parent_area_id,
                literal_column("1").label("depth"),
            )
            .where(Area.id == parent_area_id)
            .cte(name="parent_chain", recursive=True)
        )

        # Create alias for the recursive part
        parent_chain_alias = aliased(parent_chain_cte, name="pc")
        area_alias = aliased(Area, name="a")

        # Recursive part: join areas with parent_chain on parent_area_id
        recursive_part = (
            select(
                area_alias.id,
                area_alias.parent_area_id,
                (parent_chain_alias.c.depth + 1).label("depth"),
            )
            .join(
                parent_chain_alias,
                area_alias.id == parent_chain_alias.c.parent_area_id,
            )
            .where(parent_chain_alias.c.depth < max_depth)
        )

        # Union the base and recursive parts
        parent_chain_cte = parent_chain_cte.union_all(recursive_part)

        # Check if area_id exists in the parent chain (circular reference)
        cycle_check = (
            select(literal_column("1"))
            .select_from(parent_chain_cte)
            .where(parent_chain_cte.c.id == area_id)
        )
        has_cycle_query = select(exists(cycle_check))
        has_cycle_result = await self.session.execute(has_cycle_query)
        has_cycle = has_cycle_result.scalar() or False

        # Check if we hit the depth limit (which could mean infinite loop or very deep hierarchy)
        max_depth_query = select(func.max(parent_chain_cte.c.depth)).select_from(
            parent_chain_cte
        )
        max_depth_result = await self.session.execute(max_depth_query)
        reached_depth = max_depth_result.scalar() or 0
        hit_depth_limit = reached_depth >= max_depth

        return has_cycle, hit_depth_limit

    async def get_nearby_areas(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int,
        require_all_landmarks_in_radius: bool = False,
        only_verified: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[tuple[Area, int]], int]:
        """
        Get areas that have landmarks within a given radius from a point with pagination.

        Optimized with CTE for better query performance.

        Args:
            latitude: Latitude of the center point
            longitude: Longitude of the center point
            radius_meters: Search radius in meters
            require_all_landmarks_in_radius: If True, only return areas where all landmarks are within radius
            only_verified: If True, only return verified areas
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            Tuple of (list of (area, landmark_count) tuples, total count)
        """
        # Create a point from the given coordinates (SRID 4326 is WGS84)
        user_point = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)

        # CTE for landmarks within radius
        nearby_landmarks_cte = (
            select(
                Landmark.id,
                Landmark.area_id,
            )
            .where(
                ST_DWithin(
                    Landmark.location,
                    user_point,
                    radius_meters,
                    True,  # Use spheroid for accurate distance calculation
                )
            )
            .cte(name="nearby_landmarks")
        )

        # CTE for landmark counts per area within radius
        landmark_count_cte = (
            select(
                nearby_landmarks_cte.c.area_id,
                func.count(nearby_landmarks_cte.c.id).label("landmark_count"),
            )
            .group_by(nearby_landmarks_cte.c.area_id)
            .cte(name="landmark_counts")
        )

        # Base query joining areas with landmark counts
        base_query = select(Area, landmark_count_cte.c.landmark_count).join(
            landmark_count_cte, Area.id == landmark_count_cte.c.area_id
        )

        # If require_all_landmarks_in_radius, filter areas where count matches total
        if require_all_landmarks_in_radius:
            # Subquery to get total landmark count per area
            total_count_subquery = (
                select(
                    Landmark.area_id,
                    func.count(Landmark.id).label("total_count"),
                )
                .group_by(Landmark.area_id)
                .subquery()
            )

            base_query = base_query.join(
                total_count_subquery,
                Area.id == total_count_subquery.c.area_id,
            ).where(
                landmark_count_cte.c.landmark_count
                == total_count_subquery.c.total_count
            )

        # Filter by verified areas if specified
        if only_verified:
            base_query = base_query.where(Area.is_verified == True)  # noqa: E712

        # Order by landmark count descending for better UX (areas with more landmarks first)
        base_query = base_query.order_by(landmark_count_cte.c.landmark_count.desc())

        # Count query - count distinct areas from the base query
        count_query = select(func.count()).select_from(base_query.subquery())

        # Execute count query
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar_one()

        # Apply pagination to main query
        paginated_query = base_query.limit(limit).offset(offset)

        # Execute the main query
        result = await self.session.execute(paginated_query)
        areas_with_counts = list(result.all())

        return areas_with_counts, total_count
