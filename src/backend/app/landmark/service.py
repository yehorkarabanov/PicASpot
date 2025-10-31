import uuid

from geoalchemy2.elements import WKTElement

from app.area.repository import AreaRepository
from app.core.exceptions import ForbiddenError, NotFoundError
from app.user.models import User

from .repository import LandmarkRepository
from .schemas import LandmarkCreate, LandmarkResponse, LandmarkUpdate


class LandmarkService:
    """
    Service layer for managing landmark operations.

    This service handles the business logic for landmarks, which are
    points of interest within areas that users can discover and unlock.

    Currently serves as a placeholder for future landmark-related business logic.
    """

    def __init__(
        self, landmark_repository: LandmarkRepository, area_repository: AreaRepository
    ):
        """
        Initialize the LandmarkService.

        Args:
            landmark_repository: Repository instance for landmark data access.
        """
        self.landmark_repository = landmark_repository
        self.area_repository = area_repository

    async def create_landmark(
        self, landmark_data: LandmarkCreate, creator_id: uuid.UUID
    ) -> LandmarkResponse:
        """
        Create a new landmark.

        Args:
            landmark_data: Data for the new landmark.
            creator_id: ID of the user creating the landmark.

        Returns:
            The created landmark response.

        Raises:
            NotFoundError: If the area does not exist.
        """
        await self._validate_area_exists(landmark_data.area_id)

        # Convert landmark data to dict
        landmark_dict = landmark_data.model_dump(exclude={"latitude", "longitude"})
        landmark_dict["creator_id"] = creator_id

        # Create a WKT POINT from latitude and longitude for PostGIS
        # POINT(longitude latitude) - note the order!
        point_wkt = f"POINT({landmark_data.longitude} {landmark_data.latitude})"
        landmark_dict["location"] = WKTElement(point_wkt, srid=4326)

        landmark = await self.landmark_repository.create(landmark_dict)

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
        return LandmarkResponse.model_validate(landmark)

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

    async def update_landmark(
        self, landmark_id: uuid.UUID, landmark_data: LandmarkUpdate, user: User
    ) -> LandmarkResponse:
        """
        Update a landmark by its ID with the given data.

        Superusers can update any landmark. Regular users can only update landmarks they created.

        Args:
            landmark_id: The UUID of the landmark to update.
            landmark_data: The updated landmark data.
            user: The user attempting to update the landmark.

        Returns:
            LandmarkResponse: The updated landmark data.

        Raises:
            NotFoundError: If the landmark or area does not exist.
            ForbiddenError: If the user does not have permission to update the landmark.
        """
        landmark = await self.landmark_repository.get_by_id(landmark_id)
        if not landmark:
            raise NotFoundError(f"Landmark with ID {landmark_id} not found")

        if landmark.creator_id != user.id and not user.is_superuser:
            raise ForbiddenError(
                "You do not have permission to update this landmark"
            )

        # Validate area exists if area_id is being updated
        if landmark_data.area_id is not None:
            await self._validate_area_exists(landmark_data.area_id)

        # Handle location update if latitude or longitude are provided
        landmark_dict = landmark_data.model_dump(
            exclude_unset=True, exclude={"latitude", "longitude"}
        )

        # If either latitude or longitude is provided, update location
        if landmark_data.latitude is not None or landmark_data.longitude is not None:
            # Use new values if provided, otherwise keep existing
            lat = (
                landmark_data.latitude
                if landmark_data.latitude is not None
                else landmark.latitude
            )
            lon = (
                landmark_data.longitude
                if landmark_data.longitude is not None
                else landmark.longitude
            )
            point_wkt = f"POINT({lon} {lat})"
            landmark_dict["location"] = WKTElement(point_wkt, srid=4326)

        landmark = await self.landmark_repository.update(landmark_id, landmark_dict)
        return LandmarkResponse.model_validate(landmark)

