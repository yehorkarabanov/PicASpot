from typing import Any, Dict, Generic, List, Optional, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .abstract_repository import AbstractRepository

T = TypeVar("T")


class BaseRepository(AbstractRepository[T]):
    """Base repository implementation using SQLAlchemy"""

    def __init__(self, session: AsyncSession, model: type[T], pk_attr: str = "id"):
        self.session = session
        self.model = model
        self.pk_attr = pk_attr

    async def create(self, data: Dict[str, Any]) -> T:
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get_by_id(self, entity_id: Any, load_options: Optional[List[Any]] = None) -> Optional[T]:
        # Example: To fetch foreign keys efficiently, use load_options like [selectinload(Model.foreign_relationship)]
        # e.g., [selectinload(User.posts)] to load posts with the user in one query
        query = select(self.model).where(getattr(self.model, self.pk_attr) == entity_id)
        if load_options:
            query = query.options(*load_options)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_field(self, field_name: str, field_value: Any, load_options: Optional[List[Any]] = None) -> Optional[T]:
        # Example: To fetch foreign keys efficiently, use load_options like [selectinload(Model.foreign_relationship)]
        # e.g., [selectinload(Post.author)] to load the author with the post
        query = select(self.model).where(getattr(self.model, field_name) == field_value)
        if load_options:
            query = query.options(*load_options)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, filter_criteria: Optional[Dict[str, Any]] = None, load_options: Optional[List[Any]] = None) -> List[T]:
        # Example: To fetch foreign keys efficiently, use load_options like [selectinload(Model.foreign_relationship)]
        # e.g., [selectinload(User.posts)] to load posts for all users in one query
        query = select(self.model)
        if filter_criteria:
            for key, value in filter_criteria.items():
                query = query.where(getattr(self.model, key) == value)
        if load_options:
            query = query.options(*load_options)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, entity_id: Any, data: Dict[str, Any]) -> Optional[T]:
        obj = await self.session.get(self.model, entity_id)
        if not obj:
            return None
        for key, value in data.items():
            setattr(obj, key, value)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, entity_id: Any) -> bool:
        obj = await self.session.get(self.model, entity_id)
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
