import logging
from io import BytesIO

from PIL import Image

from app.kafka.schemas import UnlockVerifyMessage, UnlockVerifyResult
from app.settings import settings
from app.storage import storage_service

logger = logging.getLogger(__name__)


class VerificationService:
    """Service for verifying images using GeoMatchAI."""

    def __init__(self):
        """Initialize the verification service."""
        self.matcher = None
        self._started = False

    async def start(self) -> None:
        """Initialize GeoMatchAI matcher."""
        if self._started:
            return

        try:
            # Import GeoMatchAI - lazy import to handle potential import issues
            from geomatchai import ImageMatcher

            self.matcher = ImageMatcher(model_name=settings.GEOMATCH_MODEL_NAME)
            self._started = True
            logger.info(
                "GeoMatchAI initialized",
                extra={"model": settings.GEOMATCH_MODEL_NAME},
            )
        except Exception as e:
            logger.error(f"Failed to initialize GeoMatchAI: {e}")
            raise

    async def stop(self) -> None:
        """Cleanup verification service resources."""
        self._started = False
        self.matcher = None
        logger.info("VerificationService stopped")

    def _load_image(self, image_bytes: bytes) -> Image.Image:
        """Load image from bytes."""
        return Image.open(BytesIO(image_bytes))

    async def verify_unlock(self, message: UnlockVerifyMessage) -> UnlockVerifyResult:
        """
        Verify if user's photo matches the landmark.

        Args:
            message: The unlock verification message containing photo URLs and metadata.

        Returns:
            UnlockVerifyResult with success status and similarity score.
        """
        if not self._started or not self.matcher:
            return UnlockVerifyResult(
                user_id=message.user_id,
                landmark_id=message.landmark_id,
                photo_url=message.photo_url,
                success=False,
                error="VerificationService not initialized",
            )

        try:
            # Download both images from MinIO
            logger.info(
                "Downloading images for verification",
                extra={
                    "user_photo": message.photo_url,
                    "landmark_image": message.landmark_image,
                },
            )

            user_photo_bytes = await storage_service.get_object(message.photo_url)
            landmark_image_bytes = await storage_service.get_object(
                message.landmark_image
            )

            # Load images
            user_photo = self._load_image(user_photo_bytes)
            landmark_image = self._load_image(landmark_image_bytes)

            # Compare images using GeoMatchAI
            logger.info("Comparing images with GeoMatchAI")
            similarity_score = self.matcher.compare(user_photo, landmark_image)

            # Determine if verification passed
            is_match = similarity_score >= settings.GEOMATCH_SIMILARITY_THRESHOLD

            logger.info(
                "Image verification completed",
                extra={
                    "user_id": message.user_id,
                    "landmark_id": message.landmark_id,
                    "similarity_score": similarity_score,
                    "threshold": settings.GEOMATCH_SIMILARITY_THRESHOLD,
                    "is_match": is_match,
                },
            )

            return UnlockVerifyResult(
                user_id=message.user_id,
                landmark_id=message.landmark_id,
                photo_url=message.photo_url,
                success=is_match,
                similarity_score=similarity_score,
            )

        except Exception as e:
            logger.error(
                f"Verification failed: {e}",
                exc_info=True,
                extra={
                    "user_id": message.user_id,
                    "landmark_id": message.landmark_id,
                },
            )
            return UnlockVerifyResult(
                user_id=message.user_id,
                landmark_id=message.landmark_id,
                photo_url=message.photo_url,
                success=False,
                error=str(e),
            )


# Global singleton instance
verification_service = VerificationService()
