import logging
import random

from app.kafka.schemas import UnlockVerifyMessage, UnlockVerifyResult
from app.settings import settings
from app.storage import storage_service

logger = logging.getLogger(__name__)


class VerificationService:
    """Mock service for verifying images - returns random results for development."""

    def __init__(self):
        """Initialize the verification service."""
        self._started = False

    async def start(self) -> None:
        """Initialize mock verification service."""
        if self._started:
            return

        self._started = True
        logger.info("Mock VerificationService started")

    async def stop(self) -> None:
        """Cleanup verification service resources."""
        self._started = False
        logger.info("VerificationService stopped")

    async def verify_unlock(self, message: UnlockVerifyMessage) -> UnlockVerifyResult:
        """
        Mock verify if user's photo matches the landmark - returns random result.

        Args:
            message: The unlock verification message containing photo URLs and metadata.

        Returns:
            UnlockVerifyResult with random success status and similarity score.
        """
        if not self._started:
            return UnlockVerifyResult(
                attempt_id=message.attempt_id,
                photo_url=message.photo_url,
                success=False,
                error="VerificationService not initialized",
            )

        try:
            # Download user photo from MinIO (to simulate real behavior)
            logger.info(
                "Downloading image for mock verification",
                extra={
                    "user_photo": message.photo_url,
                },
            )
            user_photo_bytes = await storage_service.get_object(message.photo_url)

            # Mock verification: random success and similarity score
            similarity_score = random.uniform(0.0, 1.0)
            success = random.choice([True, False])

            logger.info(
                "Mock image verification completed",
                extra={
                    "attempt_id": message.attempt_id,
                    "similarity_score": similarity_score,
                    "threshold": settings.GEOMATCH_SIMILARITY_THRESHOLD,
                    "is_verified": success,
                },
            )

            return UnlockVerifyResult(
                attempt_id=message.attempt_id,
                photo_url=message.photo_url,
                success=success,
                similarity_score=similarity_score,
            )

        except Exception as e:
            logger.error(
                f"Mock verification failed: {e}",
                exc_info=True,
                extra={
                    "attempt_id": message.attempt_id,
                },
            )
            return UnlockVerifyResult(
                attempt_id=message.attempt_id,
                photo_url=message.photo_url,
                success=False,
                error=str(e),
            )


# Global singleton instance
verification_service = VerificationService()
