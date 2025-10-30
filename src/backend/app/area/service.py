import uuid

from app.user.models import User

from .repository import AreaRepository
from .schemas import AreaCreate, AreaResponse, AreaUpdate


class AreaService:
    def __init__(self, area_repository: AreaRepository):
        self.area_repository = area_repository

    async def create_area(
        self, area_data: AreaCreate, created_by: uuid.UUID
    ) -> AreaResponse:
        """Create a new area with the given data and creator ID."""
        area_dict = area_data.model_dump()
        area_dict["created_by"] = created_by
        area = await self.area_repository.create(area_dict)
        return AreaResponse.model_validate(area)

    async def get_area(self, area_id: uuid.UUID) -> AreaResponse:
        """Retrieve an area by its ID."""
        area = await self.area_repository.get_by_id(area_id)
        return AreaResponse.model_validate(area)

    async def delete_area(self, area_id: uuid.UUID, user: User) -> None:
        """Delete an area by its ID."""
        if user.is_superuser:
            await self.area_repository.delete(area_id)
            return

        area = await self.area_repository.get_by_id(area_id)
        if area.created_by != user.id:
            raise PermissionError("You do not have permission to delete this area.")
        await self.area_repository.delete(area_id)

    async def update_area(
        self, area_id: uuid.UUID, area_data: AreaUpdate, user: User
    ) -> AreaResponse:
        """Update an area by its ID with the given data."""
        area_dict = area_data.model_dump(exclude_unset=True)
        if user.is_superuser:
            area = await self.area_repository.update(area_id, area_dict)
            return AreaResponse.model_validate(area)

        area = await self.area_repository.get_by_id(area_id)
        if area.created_by != user.id:
            raise PermissionError("You do not have permission to update this area.")

        area = await self.area_repository.update(area_id, area_dict)
        return AreaResponse.model_validate(area)

    async def verify_area(self, area_id: uuid.UUID, super_user: User) -> AreaResponse:
        """Verify an area by its ID."""
        if not super_user.is_superuser:
            raise PermissionError("Only superusers can verify areas.")

        area_dict = {"is_verified": True}
        updated_area = await self.area_repository.update(area_id, area_dict)
        return AreaResponse.model_validate(updated_area)
