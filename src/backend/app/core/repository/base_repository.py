from typing import Any, TypeVar
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .abstract_repository import AbstractRepository

T = TypeVar("T")


class BaseRepository(AbstractRepository[T]):
    """
    Base repository implementation using SQLAlchemy.

    Note: Timezone handling is done at the serialization layer (Pydantic schemas),
    not in the repository. The repository returns raw database entities with UTC
    timestamps, and schemas handle timezone conversion during JSON serialization.
    """

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
        # Keep timezone for backward compatibility and potential future use
        self.timezone = timezone or ZoneInfo("UTC")

    async def create(self, data: dict[str, Any]) -> T:
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

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
        return result.scalar_one_or_none()

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
        return result.scalar_one_or_none()

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
        return list(result.scalars().all())

    async def update(self, entity_id: Any, data: dict[str, Any]) -> T | None:
        obj = await self.get_by_id(entity_id)
        if not obj:
            return None
        for key, value in data.items():
            setattr(obj, key, value)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

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
        return entity
