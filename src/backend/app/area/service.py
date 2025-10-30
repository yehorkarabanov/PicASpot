import uuid

from app.core.exceptions import BadRequestError, NotFoundError
from app.user.models import User

from .repository import AreaRepository
from .schemas import AreaCreate, AreaResponse, AreaUpdate


class AreaService:
    def __init__(self, area_repository: AreaRepository):
        self.area_repository = area_repository

    async def _validate_parent_area_exists(self, parent_area_id: uuid.UUID) -> None:
        """
        Validate that a parent area exists.

        Args:
            parent_area_id: The UUID of the parent area to validate

        Raises:
            NotFoundError: If the parent area does not exist
        """
        parent_area = await self.area_repository.get_by_id(parent_area_id)
        if not parent_area:
            raise NotFoundError(f"Parent area with ID {parent_area_id} not found")

    async def create_area(
        self, area_data: AreaCreate, created_by: uuid.UUID
    ) -> AreaResponse:
        """Create a new area with the given data and creator ID."""
        if area_data.parent_area_id:
            await self._validate_parent_area_exists(area_data.parent_area_id)

        area_dict = area_data.model_dump()
        area_dict["created_by"] = created_by
        area = await self.area_repository.create(area_dict)
        return AreaResponse.model_validate(area)

    async def get_area(self, area_id: uuid.UUID) -> AreaResponse:
        """Retrieve an area by its ID."""
        area = await self.area_repository.get_by_id(area_id)
        if not area:
            raise NotFoundError(f"Area with ID {area_id} not found")
        return AreaResponse.model_validate(area)

    async def delete_area(self, area_id: uuid.UUID, user: User) -> None:
        """Delete an area by its ID."""
        if user.is_superuser:
            deleted = await self.area_repository.delete(area_id)
            if not deleted:
                raise NotFoundError(f"Area with ID {area_id} not found")
            return

        area = await self.area_repository.get_by_id(area_id)
        if not area:
            raise NotFoundError(f"Area with ID {area_id} not found")
        if area.created_by != user.id:
            raise PermissionError("You do not have permission to delete this area.")

        deleted = await self.area_repository.delete(area_id)
        if not deleted:
            raise NotFoundError(f"Area with ID {area_id} not found")

    async def update_area(
        self, area_id: uuid.UUID, area_data: AreaUpdate, user: User
    ) -> AreaResponse:
        """Update an area by its ID with the given data."""
        area = await self.area_repository.get_by_id(area_id)
        if not area:
            raise NotFoundError(f"Area with ID {area_id} not found")

        if area.created_by != user.id and not user.is_superuser:
            raise PermissionError("You do not have permission to update this area.")

        if area_data.parent_area_id is not None:
            if area_data.parent_area_id == area_id:
                raise BadRequestError("An area cannot be its own parent")

            await self._validate_parent_area_exists(area_data.parent_area_id)

        area_dict = area_data.model_dump(exclude_unset=True)
        area = await self.area_repository.update(area_id, area_dict)
        return AreaResponse.model_validate(area)

    async def verify_area(self, area_id: uuid.UUID, super_user: User) -> AreaResponse:
        """Verify an area by its ID."""
        if not super_user.is_superuser:
            raise PermissionError("Only superusers can verify areas.")

        area_dict = {"is_verified": True}
        updated_area = await self.area_repository.update(area_id, area_dict)
        if not updated_area:
            raise NotFoundError(f"Area with ID {area_id} not found")
        return AreaResponse.model_validate(updated_area)
