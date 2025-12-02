"""
Area model factory for test data generation.

This factory creates Area model instances with realistic fake data,
including support for hierarchical relationships.
"""

import uuid

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.area.models import Area
from app.user.models import User

fake = Faker()


class AreaFactory:
    """
    Factory for creating Area instances in tests.

    This class provides methods to create areas with various configurations,
    including hierarchical (parent-child) relationships.
    """

    @staticmethod
    async def create(
        session: AsyncSession,
        creator: User,
        name: str | None = None,
        description: str | None = None,
        parent_area: Area | None = None,
        image_url: str | None = None,
        badge_url: str | None = None,
        is_verified: bool = False,
        **kwargs,
    ) -> Area:
        """
        Create an area with the given attributes.

        Args:
            session: Database session
            creator: User who creates the area
            name: Area name (auto-generated if None)
            description: Area description (auto-generated if None)
            parent_area: Parent area for hierarchical relationships
            image_url: URL to area image (auto-generated if None)
            badge_url: URL to area badge (auto-generated if None)
            is_verified: Whether the area is verified
            **kwargs: Additional area attributes

        Returns:
            Created Area instance

        Example:
            area = await AreaFactory.create(session, user)
            child_area = await AreaFactory.create(
                session, user,
                parent_area=area,
                name="Downtown"
            )
        """
        area_data = {
            "id": uuid.uuid4(),
            "creator_id": creator.id,
            "parent_area_id": parent_area.id if parent_area else None,
            "name": name or fake.city(),
            "description": description or fake.text(max_nb_chars=200),
            "image_url": image_url or fake.image_url(),
            "badge_url": badge_url or fake.image_url(),
            "is_verified": is_verified,
        }
        area_data.update(kwargs)

        area = Area(**area_data)
        session.add(area)
        await session.commit()
        await session.refresh(area)
        return area

    @staticmethod
    async def create_batch(
        session: AsyncSession,
        creator: User,
        count: int = 5,
        **kwargs,
    ) -> list[Area]:
        """
        Create multiple areas at once.

        Args:
            session: Database session
            creator: User who creates the areas
            count: Number of areas to create
            **kwargs: Common attributes for all areas

        Returns:
            List of created Area instances

        Example:
            areas = await AreaFactory.create_batch(session, user, count=10)
        """
        areas = []
        for _ in range(count):
            area = await AreaFactory.create(session, creator, **kwargs)
            areas.append(area)
        return areas

    @staticmethod
    async def create_hierarchy(
        session: AsyncSession,
        creator: User,
        depth: int = 3,
        **kwargs,
    ) -> list[Area]:
        """
        Create a hierarchical structure of areas.

        Creates a chain of parent-child areas up to the specified depth.

        Args:
            session: Database session
            creator: User who creates the areas
            depth: Number of levels in the hierarchy
            **kwargs: Common attributes for all areas

        Returns:
            List of created Area instances (parent to child order)

        Example:
            # Creates: Country -> State -> City
            hierarchy = await AreaFactory.create_hierarchy(
                session, user, depth=3
            )
            country = hierarchy[0]
            state = hierarchy[1]
            city = hierarchy[2]
        """
        areas = []
        parent = None

        for level in range(depth):
            area = await AreaFactory.create(
                session,
                creator,
                parent_area=parent,
                name=f"Level {level} - {fake.city()}",
                **kwargs,
            )
            areas.append(area)
            parent = area

        return areas

    @staticmethod
    async def create_with_children(
        session: AsyncSession,
        creator: User,
        num_children: int = 3,
        parent_name: str | None = None,
        **kwargs,
    ) -> tuple[Area, list[Area]]:
        """
        Create a parent area with multiple child areas.

        Args:
            session: Database session
            creator: User who creates the areas
            num_children: Number of child areas to create
            parent_name: Name for parent area
            **kwargs: Common attributes for all areas

        Returns:
            Tuple of (parent_area, list of child_areas)

        Example:
            parent, children = await AreaFactory.create_with_children(
                session, user, num_children=5
            )
        """
        # Create parent area
        parent = await AreaFactory.create(
            session,
            creator,
            name=parent_name,
            **kwargs,
        )

        # Create child areas
        children = []
        for i in range(num_children):
            child = await AreaFactory.create(
                session,
                creator,
                parent_area=parent,
                name=f"{parent.name} - District {i + 1}",
                **kwargs,
            )
            children.append(child)

        return parent, children

    @staticmethod
    async def create_verified_area(
        session: AsyncSession,
        creator: User,
        **kwargs,
    ) -> Area:
        """
        Create a verified area.

        Verified areas have special status in the application.
        """
        return await AreaFactory.create(
            session,
            creator,
            is_verified=True,
            **kwargs,
        )

    @staticmethod
    def generate_name() -> str:
        """Generate a random area name."""
        return fake.city()

    @staticmethod
    def generate_description() -> str:
        """Generate a random area description."""
        return fake.text(max_nb_chars=200)


__all__ = ["AreaFactory"]
