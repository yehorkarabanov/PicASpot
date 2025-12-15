import logging
import uuid
from zoneinfo import ZoneInfo

from app.core.exceptions import BadRequestError, NotFoundError
from app.kafka import kafka_producer
from app.kafka.schemas import UnlockVerifyMessage
from app.landmark.repository import LandmarkRepository
from app.storage import StorageDir, StorageService
from app.user.models import User

from .repository import UnlockRepository
from .schemas import UnlockCreate

logger = logging.getLogger(__name__)


class UnlockService:
    """
    Service layer for managing unlock operations.

    This service handles the business logic for tracking when users unlock
    landmarks or areas, including validation and achievement tracking.
    """

    def __init__(
        self,
        unlock_repository: UnlockRepository,
        landmark_repository: LandmarkRepository,
        storage: StorageService,
        timezone: ZoneInfo | None = None,
    ):
        """
        Initialize the UnlockService.

        Args:
            unlock_repository: Repository instance for unlock data access.
            landmark_repository: Repository instance for landmark data access.
            storage: Storage service for file uploads.
            kafka_producer: Kafka producer for sending verification messages.
            timezone: Client's timezone for datetime conversion in responses.
        """
        self.unlock_repository = unlock_repository
        self.landmark_repository = landmark_repository
        self.storage = storage
        self.timezone = timezone or ZoneInfo("UTC")

    async def create_unlock(self, unlock_data: UnlockCreate, user: User) -> None:
        """
        Create a new unlock (verify photo).

        Args:
            unlock_data: Data for the new unlock.
            user: The user creating the unlock.

        Returns:
            The created unlock response.

        Raises:
            NotFoundError: If the landmark does not exist.
        """
        (
            landmark,
            existing_unlock,
        ) = await self.landmark_repository.get_landmark_with_unlock_status(
            landmark_id=unlock_data.landmark_id, user_id=user.id
        )

        if not landmark:
            raise NotFoundError(f"Landmark with ID {unlock_data.landmark_id} not found")

        if existing_unlock:
            raise BadRequestError("Landmark already unlocked by this user")

        # Upload photo
        result = await self.storage.upload_file(
            file_data=await unlock_data.image_file.read(),
            original_filename=f"{user.id}_{uuid.uuid4()}_{unlock_data.image_file.filename}",
            path_prefix=StorageDir.UNLOCKS,
            content_type=unlock_data.image_file.content_type
            or "application/octet-stream",
        )
        photo_url = result["public_url"]

        # Send Kafka message for verification
        message = UnlockVerifyMessage(
            user_id=str(user.id),
            photo_url=photo_url,
            landmark_id=str(landmark.id),
            landmark_image=landmark.image_url,
            latitude=landmark.latitude,
            longitude=landmark.longitude,
            unlock_radius_meters=landmark.unlock_radius_meters,
            photo_radius_meters=landmark.photo_radius_meters,
        )
        await kafka_producer.send_unlock_verify_message(message)

        logger.info(
            "Unlock created successfully: %s by user %s", landmark.name, user.id
        )
