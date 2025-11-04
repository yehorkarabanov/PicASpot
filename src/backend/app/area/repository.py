import uuid

from sqlalchemy import exists, func, literal_column, select
from sqlalchemy.orm import aliased

from app.core.repository import BaseRepository

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
