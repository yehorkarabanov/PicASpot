import logging
import uuid
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from app.core.exceptions import BadRequestError, NotFoundError
from app.kafka import kafka_producer
from app.kafka.schemas import UnlockVerifyMessage
from app.landmark.repository import LandmarkRepository
from app.storage import StorageDir, StorageService
from app.user.models import User

from .models import AttemptStatus
from .repository import AttemptRepository, UnlockRepository
from .schemas import (
    UnlockCreate,
    UnlockListRequestParams,
    UnlockListResponse,
    UnlockRequestParams,
    UnlockResponse,
)

if TYPE_CHECKING:
    from .models import Unlock

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

        attempt = await self.attempt_repository.create(
            {
                "user_id": user.id,
                "landmark_id": landmark.id,
                "status": AttemptStatus.PENDING,
                "photo_url": photo_upload_data["public_url"],
            }
        )

        # Send Kafka message for verification
        message = UnlockVerifyMessage(
            attempt_id=str(attempt.id),
            photo_url=photo_upload_data["object_path"],
            latitude=landmark.latitude,
            longitude=landmark.longitude,
            unlock_radius_meters=landmark.unlock_radius_meters,
            photo_radius_meters=landmark.photo_radius_meters,
        )
        await kafka_producer.send_unlock_verify_message(message)

        logger.info(
            "Unlock created successfully: %s by user %s", landmark.name, user.id
        )

    async def handle_verification_result(
        self,
        attempt_id: uuid.UUID,
        success: bool,
        photo_url: str,
        similarity_score: float | None,
        error: str | None,
    ) -> None:
        """
        Handle the result of a verification attempt.

        Args:
            attempt_id: ID of the verification attempt.
            success: Whether the verification was successful.
            photo_url: URL of the photo used for verification.
            similarity_score: Similarity score from the verification process.
            error: Error message if the verification failed.
        """
        attempt = await self.attempt_repository.get_by_id(attempt_id)

        if not attempt:
            logger.error("No pending attempt found for attempt ID %s", attempt_id)
            return

        user_id = attempt.user_id
        landmark_id = attempt.landmark_id

        if error:
            attempt.error_message = error
            attempt.status = AttemptStatus.FAILED
            await self.attempt_repository.update(attempt.id, attempt.__dict__)
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

    async def get_unlock_by_id(
        self, landmark_id: str, user: User, params: UnlockRequestParams
    ) -> UnlockResponse:
        """
        Retrieve an unlock by landmark ID for the current user.

        Args:
            landmark_id: The landmark UUID (composite key uses user_id + landmark_id).
            user: The current user.
            params: Request parameters for conditional loading.

        Returns:
            The unlock response with optional related data.

        Raises:
            NotFoundError: If the unlock does not exist.
        """
        unlock = await self.unlock_repository.get_unlock_with_relations(
            user_id=user.id,
            landmark_id=uuid.UUID(landmark_id),
            load_attempt=params.load_attempt_data,
            load_landmark=params.load_landmark_data,
            load_area=params.load_area_data and params.load_landmark_data,
        )

        if not unlock:
            raise NotFoundError(f"Unlock for landmark {landmark_id} not found")

        return self._build_unlock_response(unlock, params)

    async def list_unlocks(
        self, user: User, params: UnlockListRequestParams
    ) -> UnlockListResponse:
        """
        List all unlocks for a user with pagination.

        Args:
            user: The current user.
            params: Request parameters for pagination and conditional loading.

        Returns:
            Paginated list of unlock responses.
        """
        offset = (params.page - 1) * params.page_size

        unlocks, total = await self.unlock_repository.get_user_unlocks_paginated(
            user_id=user.id,
            limit=params.page_size,
            offset=offset,
            load_attempt=params.load_attempt_data,
            load_landmark=params.load_landmark_data,
            load_area=params.load_area_data and params.load_landmark_data,
        )

        unlock_responses = [
            self._build_unlock_response(unlock, params) for unlock in unlocks
        ]

        total_pages = max(1, (total + params.page_size - 1) // params.page_size)

        return UnlockListResponse(
            unlocks=unlock_responses,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
            count=len(unlock_responses),
        )

    def _build_unlock_response(
        self, unlock: "Unlock", params: UnlockRequestParams
    ) -> UnlockResponse:
        """
        Build an UnlockResponse from an Unlock entity with optional nested data.

        Args:
            unlock: The unlock entity with potentially loaded relations.
            params: Request parameters for conditional field inclusion.

        Returns:
            The formatted unlock response.
        """
        from app.area.schemas import AreaResponse
        from app.landmark.schemas import LandmarkResponse

        from .schemas import AttemptResponse

        area_response = None
        landmark_response = None
        attempt_response = None

        if params.load_landmark_data and unlock.landmark:
            landmark_response = LandmarkResponse.model_validate_with_timezone(
                unlock.landmark, self.timezone
            )
            if params.load_area_data and unlock.landmark.area:
                area_response = AreaResponse.model_validate_with_timezone(
                    unlock.landmark.area, self.timezone
                )

        if params.load_attempt_data and unlock.attempt:
            attempt_response = AttemptResponse.model_validate_with_timezone(
                unlock.attempt, self.timezone
            )

        return UnlockResponse(
            user_id=unlock.user_id,
            landmark_id=unlock.landmark_id,
            attempt_id=unlock.attempt_id,
            area=area_response,
            landmark=landmark_response,
            attempt=attempt_response,
            photo_url=unlock.photo_url,
            is_posted_to_feed=unlock.is_posted_to_feed,
            unlocked_at=unlock.unlocked_at.astimezone(self.timezone),
            updated_at=unlock.updated_at.astimezone(self.timezone),
        )
