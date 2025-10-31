import uuid

from geoalchemy2.elements import WKTElement

from app.area.repository import AreaRepository
from app.core.exceptions import NotFoundError

from .repository import LandmarkRepository
from .schemas import LandmarkCreate, LandmarkResponse


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

