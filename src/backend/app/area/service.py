import logging
import uuid
from zoneinfo import ZoneInfo

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.settings import settings
from app.storage import StorageDir, StorageService
from app.user.models import User

from .repository import AreaRepository
from .schemas import AreaCreate, AreaResponse, AreaUpdate

logger = logging.getLogger(__name__)


class AreaService:
    """
    Service layer for managing area operations.

    This service handles the business logic for creating, reading, updating,
    and deleting areas, including permission checks and validation.
    """

    def __init__(
        self,
        area_repository: AreaRepository,
        storage: StorageService,
        timezone: ZoneInfo | None = None,
    ):
        """
        Initialize the AreaService.

        Args:
            area_repository: Repository instance for area data access.
            timezone: Client's timezone for datetime conversion in responses.
        """
        self.area_repository = area_repository
        self.storage = storage
        self.timezone = timezone or ZoneInfo("UTC")

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

    async def create_area(self, area_data: AreaCreate, user: User) -> AreaResponse:
        """
        Create a new area with the given data.

        If user is a superuser, the area will be automatically verified.

        Args:
            area_data: The area creation data containing name, description, etc.
            user: The user creating the area.

        Returns:
            AreaResponse: The created area data.

        Raises:
            NotFoundError: If the parent area does not exist.
        """
        if area_data.parent_area_id:
            await self._validate_parent_area_exists(area_data.parent_area_id)

        area_dict = area_data.model_dump(exclude={"image_file", "badge_file"})

        # TODO: Refactor file upload logic to a separate utility/helper if reused elsewhere
        if area_data.image_file:
            result = await self.storage.upload_file(
                file_data=await area_data.image_file.read(),
                original_filename=area_data.image_file.filename,
                path_prefix=StorageDir.AREAS,
                content_type=area_data.image_file.content_type
                or "application/octet-stream",
            )
            area_dict["image_url"] = result["public_url"]
        else:
            area_dict["image_url"] = settings.DEFAULT_AREA_IMAGE_URL

        if area_data.badge_file:
            result = await self.storage.upload_file(
                file_data=await area_data.badge_file.read(),
                original_filename=area_data.badge_file.filename,
                path_prefix=StorageDir.AREAS,
                content_type=area_data.badge_file.content_type
                or "application/octet-stream",
            )
            area_dict["badge_url"] = result["public_url"]
        else:
            area_dict["badge_url"] = settings.DEFAULT_AREA_IMAGE_URL

        area_dict["creator_id"] = user.id

        # Automatically verify areas created by superusers
        if user.is_superuser:
            area_dict["is_verified"] = True
            logger.info("Area will be auto-verified (created by superuser %s)", user.id)

        area = await self.area_repository.create(area_dict)
        logger.info("Area created successfully: %s by user %s", area.name, user.id)

        return AreaResponse.model_validate_with_timezone(area, self.timezone)

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

        return AreaResponse.model_validate_with_timezone(area, self.timezone)

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
        logger.info("Area deleted: %s by user %s", area.name, user.username)

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

        # Remove file objects from dict as they shouldn't be stored directly
        area_dict.pop("image_file", None)
        area_dict.pop("badge_file", None)

        # Filter out None values to prevent setting required fields to null
        # Only keep None for parent_area_id (which can be explicitly set to null)
        area_dict = {
            k: v for k, v in area_dict.items() if v is not None or k == "parent_area_id"
        }

        if area_data.image_file:
            result = await self.storage.upload_file(
                file_data=await area_data.image_file.read(),
                original_filename=area_data.image_file.filename,
                path_prefix=StorageDir.AREAS,
                content_type=area_data.image_file.content_type
                or "application/octet-stream",
            )
            area_dict["image_url"] = result["public_url"]
        if area_data.badge_file:
            result = await self.storage.upload_file(
                file_data=await area_data.badge_file.read(),
                original_filename=area_data.badge_file.filename,
                path_prefix=StorageDir.AREAS,
                content_type=area_data.badge_file.content_type
                or "application/octet-stream",
            )
            area_dict["badge_url"] = result["public_url"]
        area = await self.area_repository.update(area_id, area_dict)
        logger.info("Area updated: %s by user %s", area.name, user.username)

        return AreaResponse.model_validate_with_timezone(area, self.timezone)

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
        logger.info(
            "Area verified: %s by superuser %s", updated_area.name, super_user.username
        )

        return AreaResponse.model_validate_with_timezone(updated_area, self.timezone)
