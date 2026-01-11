import logging
import uuid
from zoneinfo import ZoneInfo

from app.core.exceptions import BadRequestError, NotFoundError
from app.kafka import kafka_producer
from app.kafka.schemas import UnlockVerifyMessage
from app.landmark.repository import LandmarkRepository
from app.storage import StorageDir, StorageService
from app.user.models import User

from .models import AttemptStatus
from .repository import AttemptRepository, UnlockRepository
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
        attempt_repository: AttemptRepository,
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
        self.attempt_repository = attempt_repository
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
        photo_upload_data = await self.storage.upload_file(
            file_data=await unlock_data.image_file.read(),
            original_filename=f"{user.id}_{uuid.uuid4()}_{unlock_data.image_file.filename}",
            path_prefix=StorageDir.UNLOCKS,
            content_type=unlock_data.image_file.content_type
            or "application/octet-stream",
        )

        # Send Kafka message for verification
        message = UnlockVerifyMessage(
            user_id=str(user.id),
            photo_url=photo_upload_data["object_path"],
            landmark_id=str(landmark.id),
            latitude=landmark.latitude,
            longitude=landmark.longitude,
            unlock_radius_meters=landmark.unlock_radius_meters,
            photo_radius_meters=landmark.photo_radius_meters,
        )
        await kafka_producer.send_unlock_verify_message(message)

        await self.attempt_repository.create(
            {
                "user_id": user.id,
                "landmark_id": landmark.id,
                "status": AttemptStatus.PENDING,
                "photo_url": photo_upload_data["public_url"],
            }
        )

        logger.info(
            "Unlock created successfully: %s by user %s", landmark.name, user.id
        )

    async def handle_verification_result(
        self,
        user_id: uuid.UUID,
        landmark_id: uuid.UUID,
        success: bool,
        photo_url: str,
        similarity_score: float | None,
        error: str | None,
    ) -> None:
        """
        Handle the result of a verification attempt.

        Args:
            user_id: ID of the user who attempted the unlock.
            landmark_id: ID of the landmark being unlocked.
            success: Whether the verification was successful.
            photo_url: URL of the photo used for verification.
            similarity_score: Similarity score from the verification process.
            error: Error message if the verification failed.
        """
        attempt = await self.attempt_repository.get_by_user_and_landmark(
            user_id=user_id, landmark_id=landmark_id
        )

        if not attempt:
            logger.error(
                "No pending attempt found for user %s and landmark %s",
                user_id,
                landmark_id,
            )
            return

        if error:
            attempt.error_message = error
            attempt.status = AttemptStatus.FAILED
            await attempt.save()
            logger.info(
                "Unlock failed for user %s at landmark %s: %s",
                user_id,
                landmark_id,
                error,
            )
            return

        attempt.similarity_score = similarity_score

        if success:
            await self.unlock_repository.create(
                {
                    "user_id": user_id,
                    "landmark_id": landmark_id,
                    "photo_url": photo_url,
                    "attempt_id": attempt.id,
                }
            )
            attempt.status = AttemptStatus.SUCCESS
            logger.info(
                "Unlock successful for user %s at landmark %s", user_id, landmark_id
            )
        else:
            attempt.status = AttemptStatus.FAILED
            logger.info(
                "Unlock failed for user %s at landmark %s: %s",
                user_id,
                landmark_id,
                error,
            )

        await self.attempt_repository.update(attempt.id, attempt.__dict__)
