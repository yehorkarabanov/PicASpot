import uuid

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.user.models import User

from .repository import AreaRepository
from .schemas import AreaCreate, AreaResponse, AreaUpdate


class AreaService:
    """
    Service layer for managing area operations.

    This service handles the business logic for creating, reading, updating,
    and deleting areas, including permission checks and validation.
    """

    def __init__(self, area_repository: AreaRepository):
        """
        Initialize the AreaService.

        Args:
            area_repository: Repository instance for area data access.
        """
        self.area_repository = area_repository

    async def _validate_parent_area_exists(self, parent_area_id: uuid.UUID) -> None:
        """
        Validate that a parent area exists.

        Args:
            parent_area_id: The UUID of the parent area to validate.

        Raises:
            NotFoundError: If the parent area does not exist.
        """
        parent_area = await self.area_repository.get_by_id(parent_area_id)
        if not parent_area:
            raise NotFoundError(f"Parent area with ID {parent_area_id} not found")

    async def _check_circular_parent_reference(
        self, area_id: uuid.UUID, parent_area_id: uuid.UUID
    ) -> None:
        """
        Check if setting a parent would create a circular reference.

        Args:
            area_id: The UUID of the area being updated.
            parent_area_id: The UUID of the proposed parent area.

        Raises:
            BadRequestError: If a circular reference would be created or if
                the hierarchy is too deep to safely validate.
        """
        if area_id == parent_area_id:
            raise BadRequestError("An area cannot be its own parent")

        (
            has_circular_ref,
            hit_depth_limit,
        ) = await self.area_repository.check_circular_reference(area_id, parent_area_id)

        if has_circular_ref:
            raise BadRequestError(
                "Setting this parent would create a circular reference"
            )

        if hit_depth_limit:
            raise BadRequestError("Cannot set parent: hierarchy depth limit reached. ")

    async def create_area(
        self, area_data: AreaCreate, creator_id: uuid.UUID
    ) -> AreaResponse:
        """
        Create a new area with the given data and creator ID.

        Args:
            area_data: The area creation data containing name, description, etc.
            creator_id: The UUID of the user creating the area.

        Returns:
            AreaResponse: The created area data.

        Raises:
            NotFoundError: If the parent area does not exist.
        """
        if area_data.parent_area_id:
            await self._validate_parent_area_exists(area_data.parent_area_id)

        area_dict = area_data.model_dump()
        area_dict["creator_id"] = creator_id
        area = await self.area_repository.create(area_dict)
        return AreaResponse.model_validate(area)

    async def get_area(self, area_id: uuid.UUID) -> AreaResponse:
        """
        Retrieve an area by its ID.

        Args:
            area_id: The UUID of the area to retrieve.

        Returns:
            AreaResponse: The area data.

        Raises:
            NotFoundError: If the area does not exist.
        """
        area = await self.area_repository.get_by_id(area_id)
        if not area:
            raise NotFoundError(f"Area with ID {area_id} not found")
        return AreaResponse.model_validate(area)

    async def delete_area(self, area_id: uuid.UUID, user: User) -> None:
        """
        Delete an area by its ID.

        Superusers can delete any area. Regular users can only delete areas they created.

        Args:
            area_id: The UUID of the area to delete.
            user: The user attempting to delete the area.

        Raises:
            NotFoundError: If the area does not exist.
            ForbiddenError: If the user does not have permission to delete the area.
        """
        area = await self.area_repository.get_by_id(area_id)
        if not area:
            raise NotFoundError(f"Area with ID {area_id} not found")

        if not user.is_superuser and area.creator_id != user.id:
            raise ForbiddenError("You do not have permission to delete this area")

        deleted = await self.area_repository.delete(area_id)
        if not deleted:
            raise NotFoundError(f"Area with ID {area_id} not found")

    async def update_area(
        self, area_id: uuid.UUID, area_data: AreaUpdate, user: User
    ) -> AreaResponse:
        """
        Update an area by its ID with the given data.

        Superusers can update any area. Regular users can only update areas they created.

        Args:
            area_id: The UUID of the area to update.
            area_data: The updated area data.
            user: The user attempting to update the area.

        Returns:
            AreaResponse: The updated area data.

        Raises:
            NotFoundError: If the area or parent area does not exist.
            ForbiddenError: If the user does not have permission to update the area.
            BadRequestError: If the update would create invalid relationships (e.g., circular parent reference).
        """
        area = await self.area_repository.get_by_id(area_id)
        if not area:
            raise NotFoundError(f"Area with ID {area_id} not found")

        if area.creator_id != user.id and not user.is_superuser:
            raise ForbiddenError("You do not have permission to update this area")

        if area_data.parent_area_id is not None:
            await self._check_circular_parent_reference(
                area_id, area_data.parent_area_id
            )
            await self._validate_parent_area_exists(area_data.parent_area_id)

        area_dict = area_data.model_dump(exclude_unset=True)
        area = await self.area_repository.update(area_id, area_dict)
        return AreaResponse.model_validate(area)

    async def verify_area(self, area_id: uuid.UUID, super_user: User) -> AreaResponse:
        """
        Verify an area by its ID.

        Only superusers can verify areas. Verification is typically used to mark
        areas as officially recognized or approved.

        Args:
            area_id: The UUID of the area to verify.
            super_user: The superuser attempting to verify the area.

        Returns:
            AreaResponse: The verified area data.

        Raises:
            ForbiddenError: If the user is not a superuser.
            NotFoundError: If the area does not exist.
        """
        if not super_user.is_superuser:
            raise ForbiddenError("Only superusers can verify areas")

        area_dict = {"is_verified": True}
        updated_area = await self.area_repository.update(area_id, area_dict)
        if not updated_area:
            raise NotFoundError(f"Area with ID {area_id} not found")
        return AreaResponse.model_validate(updated_area)
