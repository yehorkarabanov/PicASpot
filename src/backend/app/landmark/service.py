import logging
import uuid
from zoneinfo import ZoneInfo

from geoalchemy2.elements import WKTElement

from app.area.repository import AreaRepository
from app.core.exceptions import ForbiddenError, NotFoundError
from app.settings import settings
from app.storage import StorageDir, StorageService
from app.user.models import User

from .repository import LandmarkRepository
from .schemas import (
    LandmarkCreate,
    LandmarkNearbyRequest,
    LandmarkResponse,
    LandmarkUpdate,
    NearbyLandmarksListResponse,
)

logger = logging.getLogger(__name__)


class LandmarkService:
    """
    Service layer for managing landmark operations.

    This service handles the business logic for landmarks, which are
    points of interest within areas that users can discover and unlock.

    Currently serves as a placeholder for future landmark-related business logic.
    """

    def __init__(
        self,
        landmark_repository: LandmarkRepository,
        area_repository: AreaRepository,
        storage: StorageService,
        timezone: ZoneInfo | None = None,
    ):
        """
        Initialize the LandmarkService.

        Args:
            landmark_repository: Repository instance for landmark data access.
            area_repository: Repository instance for area data access.
            storage: Storage service for file uploads.
            timezone: Client's timezone for datetime conversion in responses.
        """
        self.landmark_repository = landmark_repository
        self.area_repository = area_repository
        self.storage = storage
        self.timezone = timezone or ZoneInfo("UTC")

    async def create_landmark(
        self, landmark_data: LandmarkCreate, user: User
    ) -> LandmarkResponse:
        """
        Create a new landmark.

        Args:
            landmark_data: Data for the new landmark.
            user: The user creating the landmark.

        Returns:
            The created landmark response.

        Raises:
            NotFoundError: If the area does not exist.
        """
        await self._validate_area_exists(landmark_data.area_id)

        # Convert landmark data to dict
        landmark_dict = landmark_data.model_dump(
            exclude={
                "latitude",
                "longitude",
                "image_file",
                "hint_image_file",
                "photo_latitude",
                "photo_longitude",
            }
        )
        landmark_dict["creator_id"] = user.id

        # TODO: Refactor file upload logic to a separate utility/helper if reused elsewhere
        if landmark_data.image_file:
            result = await self.storage.upload_file(
                file_data=await landmark_data.image_file.read(),
                original_filename=landmark_data.image_file.filename,
                path_prefix=StorageDir.LANDMARKS,
                content_type=landmark_data.image_file.content_type
                or "application/octet-stream",
            )
            landmark_dict["image_url"] = result["public_url"]
        else:
            landmark_dict["image_url"] = settings.DEFAULT_LANDMARK_IMAGE_URL

        if landmark_data.hint_image_file:
            result = await self.storage.upload_file(
                file_data=await landmark_data.hint_image_file.read(),
                original_filename=landmark_data.hint_image_file.filename,
                path_prefix=StorageDir.LANDMARKS,
                content_type=landmark_data.hint_image_file.content_type
                or "application/octet-stream",
            )
            landmark_dict["hint_image_url"] = result["public_url"]

        # Create a WKT POINT from latitude and longitude for PostGIS
        # POINT(longitude latitude) - note the order!
        point_wkt = f"POINT({landmark_data.longitude} {landmark_data.latitude})"
        landmark_dict["location"] = WKTElement(point_wkt, srid=4326)

        if (
            landmark_data.photo_longitude is not None
            and landmark_data.photo_latitude is not None
        ):
            photo_point_wkt = (
                f"POINT({landmark_data.photo_longitude} {landmark_data.photo_latitude})"
            )
            landmark_dict["photo_location"] = WKTElement(photo_point_wkt, srid=4326)

        landmark = await self.landmark_repository.create(landmark_dict)

        logger.info(
            "Landmark created successfully: %s by user %s", landmark.name, user.id
        )
        return LandmarkResponse.model_validate(landmark)

    async def _validate_area_exists(self, area_id: uuid.UUID) -> None:
        """
        Validate that an area exists.

        Args:
            area_id: The UUID of the area to validate.

        Raises:
            NotFoundError: If the area does not exist.
        """
        area = await self.area_repository.get_by_id(area_id)
        if not area:
            raise NotFoundError(f"Area with ID {area_id} not found")

    async def get_landmark(self, landmark_id: uuid.UUID) -> LandmarkResponse:
        """
        Retrieve a landmark by its ID.

        Args:
            landmark_id: The UUID of the landmark to retrieve.

        Returns:
            LandmarkResponse: The landmark data.

        Raises:
            NotFoundError: If the landmark does not exist.
        """
        landmark = await self.landmark_repository.get_by_id(landmark_id)
        if not landmark:
            raise NotFoundError(f"Landmark with ID {landmark_id} not found")
        return LandmarkResponse.model_validate_with_timezone(landmark, self.timezone)

    async def delete_landmark(self, landmark_id: uuid.UUID, user: User) -> None:
        """
        Delete a landmark by its ID.

        Superusers can delete any landmark. Regular users can only delete landmarks they created.

        Args:
            landmark_id: The UUID of the landmark to delete.
            user: The user attempting to delete the landmark.

        Raises:
            NotFoundError: If the landmark does not exist.
            ForbiddenError: If the user does not have permission to delete the landmark.
        """
        landmark = await self.landmark_repository.get_by_id(landmark_id)
        if not landmark:
            raise NotFoundError(f"Landmark with ID {landmark_id} not found")

        if not user.is_superuser and landmark.creator_id != user.id:
            raise ForbiddenError("You do not have permission to delete this landmark")

        deleted = await self.landmark_repository.delete(landmark_id)
        if not deleted:
            raise NotFoundError(f"Landmark with ID {landmark_id} not found")
        logger.info("Landmark deleted: %s by user %s", landmark.name, user.username)

    async def update_landmark(
        self,
        landmark_id: uuid.UUID,
        landmark_data: LandmarkUpdate,
        user: User,
    ) -> LandmarkResponse:
        """
        Update an existing landmark.

        Args:
            landmark_id: ID of the landmark to update.
            landmark_data: Data to update.
            user: The user requesting the update.

        Returns:
            The updated landmark response.

        Raises:
            NotFoundError: If the landmark does not exist.
            ForbiddenError: If the user is not the creator of the landmark.
        """
        landmark = await self.landmark_repository.get(landmark_id)
        if not landmark:
            raise NotFoundError(f"Landmark with ID {landmark_id} not found")

        if landmark.creator_id != user.id:
            raise ForbiddenError("You can only update landmarks you created")

        # Convert update data to dict, excluding None values
        update_dict = landmark_data.model_dump(
            exclude_unset=True,
            exclude={
                "latitude",
                "longitude",
                "image_file",
                "hint_image_file",
                "photo_latitude",
                "photo_longitude",
            },
        )

        # Handle file upload if provided
        if landmark_data.image_file:
            result = await self.storage.upload_file(
                file_data=await landmark_data.image_file.read(),
                original_filename=landmark_data.image_file.filename,
                path_prefix=StorageDir.LANDMARKS,
                content_type=landmark_data.image_file.content_type
                or "application/octet-stream",
            )
            update_dict["image_url"] = result["public_url"]

        if landmark_data.hint_image_file:
            result = await self.storage.upload_file(
                file_data=await landmark_data.hint_image_file.read(),
                original_filename=landmark_data.hint_image_file.filename,
                path_prefix=StorageDir.LANDMARKS,
                content_type=landmark_data.hint_image_file.content_type
                or "application/octet-stream",
            )
            update_dict["hint_image_url"] = result["public_url"]

        # Handle location update if provided
        if landmark_data.latitude is not None and landmark_data.longitude is not None:
            point_wkt = f"POINT({landmark_data.longitude} {landmark_data.latitude})"
            update_dict["location"] = WKTElement(point_wkt, srid=4326)

        if (
            landmark_data.photo_latitude is not None
            and landmark_data.photo_longitude is not None
        ):
            photo_point_wkt = (
                f"POINT({landmark_data.photo_longitude} {landmark_data.photo_latitude})"
            )
            update_dict["photo_location"] = WKTElement(photo_point_wkt, srid=4326)

        landmark = await self.landmark_repository.update(landmark_id, update_dict)

        logger.info("Landmark updated successfully: %s", landmark_id)
        return LandmarkResponse.model_validate(landmark)

    async def get_nearby_landmarks(
        self,
        data: LandmarkNearbyRequest,
        user: User,
    ) -> NearbyLandmarksListResponse:
        """
        Get nearby landmarks with unlock status and area information.

        Args:
            data: Request data containing coordinates and filters
            user: Current user

        Returns:
            NearbyLandmarksListResponse with validated Pydantic models and pagination metadata
        """
        # Calculate offset from page number
        offset = (data.page - 1) * data.page_size

        (
            landmarks_with_status,
            total_count,
        ) = await self.landmark_repository.get_nearby_landmarks(
            latitude=data.latitude,
            longitude=data.longitude,
            radius_meters=data.radius_meters,
            user_id=user.id,
            area_id=data.area_id,
            only_verified=data.only_verified,
            load_from_same_area=data.load_from_same_area,
            limit=data.page_size,
            offset=offset,
        )

        # Use optimized batch validation via schema factory method
        response = NearbyLandmarksListResponse.from_orm_list(
            items=landmarks_with_status,
            timezone=self.timezone,
            total=total_count,
            page=data.page,
            page_size=data.page_size,
        )

        logger.info(
            "Retrieved %d/%d nearby landmarks for user %s at (%.6f, %.6f) within %dm (page %d, size %d)",
            len(landmarks_with_status),
            total_count,
            user.username,
            data.latitude,
            data.longitude,
            data.radius_meters,
            data.page,
            data.page_size,
        )

        return response

    async def get_landmarks_by_area(
        self,
        area_id: uuid.UUID,
        user: User,
        page: int = 1,
        page_size: int = 50,
        only_verified: bool = False,
    ) -> NearbyLandmarksListResponse:
        """
        Get landmarks for a specific area.

        Args:
            area_id: Area ID
            user: Current user
            page: Page number
            page_size: Page size
            only_verified: Only return if area is verified

        Returns:
            NearbyLandmarksListResponse
        """
        offset = (page - 1) * page_size

        (
            landmarks_with_status,
            total_count,
        ) = await self.landmark_repository.get_landmarks_by_area(
            area_id=area_id,
            user_id=user.id,
            only_verified=only_verified,
            limit=page_size,
            offset=offset,
        )

        return NearbyLandmarksListResponse.from_orm_list(
            items=landmarks_with_status,
            timezone=self.timezone,
            total=total_count,
            page=page,
            page_size=page_size,
        )
