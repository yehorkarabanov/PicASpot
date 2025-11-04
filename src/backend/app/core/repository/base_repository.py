from typing import Any, TypeVar
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import convert_utc_to_timezone

from .abstract_repository import AbstractRepository

T = TypeVar("T")


class BaseRepository(AbstractRepository[T]):
    """Base repository implementation using SQLAlchemy"""

    def __init__(
        self,
        session: AsyncSession,
        model: type[T],
        pk_attr: str = "id",
        timezone: ZoneInfo | None = None,
    ):
        self.session = session
        self.model = model
        self.pk_attr = pk_attr
        self.timezone = timezone or ZoneInfo("UTC")

    def _convert_timestamps(self, entity: T) -> T:
        """
        Convert UTC timestamps to the repository's timezone.
        Only converts if timezone is not UTC and entity has timestamp fields.

        Args:
            entity: The entity to convert timestamps for

        Returns:
            The entity with converted timestamps (modified in place)
        """
        if self.timezone.key == "UTC":
            return entity

        # Check for common timestamp fields and convert them
        for field_name in ["created_at", "updated_at"]:
            if hasattr(entity, field_name):
                utc_value = getattr(entity, field_name)
                if utc_value:
                    converted_value = convert_utc_to_timezone(utc_value, self.timezone)
                    setattr(entity, field_name, converted_value)

        return entity

    async def create(self, data: dict[str, Any]) -> T:
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return self._convert_timestamps(obj)

    async def get_by_id(
        self, entity_id: Any, load_options: list[Any] | None = None
    ) -> T | None:
        # Example: To fetch foreign keys efficiently, use load_options like
        # [selectinload(Model.foreign_relationship)]
        # e.g., [selectinload(User.posts)] to load posts with the user in one query
        query = select(self.model).where(getattr(self.model, self.pk_attr) == entity_id)
        if load_options:
            query = query.options(*load_options)
        result = await self.session.execute(query)
        entity = result.scalar_one_or_none()
        return self._convert_timestamps(entity) if entity else None

    async def get_by_field(
        self,
        field_name: str,
        field_value: Any,
        load_options: list[Any] | None = None,
    ) -> T | None:
        # Example: To fetch foreign keys efficiently, use load_options like
        # [selectinload(Model.foreign_relationship)]
        # e.g., [selectinload(Post.author)] to load the author with the post
        query = select(self.model).where(getattr(self.model, field_name) == field_value)
        if load_options:
            query = query.options(*load_options)
        result = await self.session.execute(query)
        entity = result.scalar_one_or_none()
        return self._convert_timestamps(entity) if entity else None

    async def get_all(
        self,
        filter_criteria: dict[str, Any] | None = None,
        load_options: list[Any] | None = None,
    ) -> list[T]:
        # Example: To fetch foreign keys efficiently, use load_options like
        # [selectinload(Model.foreign_relationship)]
        # e.g., [selectinload(User.posts)] to load posts for all users in one query
        query = select(self.model)
        if filter_criteria:
            for key, value in filter_criteria.items():
                query = query.where(getattr(self.model, key) == value)
        if load_options:
            query = query.options(*load_options)
        result = await self.session.execute(query)
        entities = list(result.scalars().all())
        return [self._convert_timestamps(entity) for entity in entities]

    async def update(self, entity_id: Any, data: dict[str, Any]) -> T | None:
        obj = await self.get_by_id(entity_id)
        if not obj:
            return None
        for key, value in data.items():
            setattr(obj, key, value)
        await self.session.commit()
        await self.session.refresh(obj)
        return self._convert_timestamps(obj)

    async def delete(self, entity_id: Any) -> bool:
        obj = await self.get_by_id(entity_id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.commit()
        return True

    async def save(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return self._convert_timestamps(entity)
