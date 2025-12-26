import logging
from collections.abc import AsyncGenerator
from io import BytesIO

from PIL import Image

from app.kafka.schemas import UnlockVerifyMessage, UnlockVerifyResult
from app.settings import settings
from app.storage import storage_service

logger = logging.getLogger(__name__)


class LandmarkImageFetcher:
    """
    Custom fetcher for GeoMatchAI that provides landmark images from MinIO storage.

    This fetcher yields the landmark reference image stored in MinIO,
    allowing GeoMatchAI to build a gallery for verification.

    Implements the BaseFetcher interface from geomatchai.fetchers.
    """

    def __init__(self, landmark_image_bytes: bytes):
        """
        Initialize with landmark image bytes.

        Args:
            landmark_image_bytes: The landmark reference image as bytes.
        """
        self.landmark_image_bytes = landmark_image_bytes

    async def get_images(
        self, lat: float, lon: float, num_images: int = 20
    ) -> AsyncGenerator[Image.Image, None]:
        """
        Yield the landmark image for gallery building.

        Args:
            lat: Latitude (unused, we use stored image).
            lon: Longitude (unused, we use stored image).
            num_images: Number of images to return (we return 1).

        Yields:
            The landmark reference image.
        """
        image = Image.open(BytesIO(self.landmark_image_bytes))
        # Convert to RGB if necessary (some images might be RGBA or grayscale)
        if image.mode != "RGB":
            image = image.convert("RGB")
        yield image


class VerificationService:
    """Service for verifying images using GeoMatchAI."""

    def __init__(self):
        """Initialize the verification service."""
        self._started = False
        self._geomatchai_available = False

    async def start(self) -> None:
        """Initialize GeoMatchAI configuration."""
        if self._started:
            return

        try:
            # Import GeoMatchAI and configure it
            from geomatchai import config

            # Configure GeoMatchAI settings
            config.set_device(settings.GEOMATCH_DEVICE)
            config.set_log_level(settings.GEOMATCH_LOG_LEVEL)

            # Set Mapillary API key if provided (for potential future use)
            if settings.MAPILLARY_API_KEY:
                config.set_mapillary_api_key(settings.MAPILLARY_API_KEY)

            self._geomatchai_available = True
            self._started = True

            logger.info(
                "GeoMatchAI configured",
                extra={
                    "device": settings.GEOMATCH_DEVICE,
                    "threshold": settings.GEOMATCH_SIMILARITY_THRESHOLD,
                    "model_type": settings.GEOMATCH_MODEL_TYPE,
                },
            )
        except ImportError as e:
            logger.error(f"GeoMatchAI not installed: {e}")
            self._geomatchai_available = False
            self._started = True  # Mark as started but without GeoMatchAI
        except Exception as e:
            logger.error(f"Failed to configure GeoMatchAI: {e}")
            raise

    async def stop(self) -> None:
        """Cleanup verification service resources."""
        self._started = False
        self._geomatchai_available = False
        logger.info("VerificationService stopped")

    async def verify_unlock(self, message: UnlockVerifyMessage) -> UnlockVerifyResult:
        """
        Verify if user's photo matches the landmark using GeoMatchAI.

        Args:
            message: The unlock verification message containing photo URLs and metadata.

        Returns:
            UnlockVerifyResult with success status and similarity score.
        """
        if not self._started:
            return UnlockVerifyResult(
                user_id=message.user_id,
                landmark_id=message.landmark_id,
                photo_url=message.photo_url,
                success=False,
                error="VerificationService not initialized",
            )

        if not self._geomatchai_available:
            return UnlockVerifyResult(
                user_id=message.user_id,
                landmark_id=message.landmark_id,
                photo_url=message.photo_url,
                success=False,
                error="GeoMatchAI library not available",
            )

        try:
            # Import GeoMatchAI for verification
            from geomatchai import GeoMatchAI

            # Download images from MinIO
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

            # Create a custom fetcher with the landmark image
            fetcher = LandmarkImageFetcher(landmark_image_bytes)

            # Create GeoMatchAI verifier with our fetcher
            verifier = await GeoMatchAI.create(
                fetcher=fetcher,
                threshold=settings.GEOMATCH_SIMILARITY_THRESHOLD,
                device=settings.GEOMATCH_DEVICE,
                model_type=settings.GEOMATCH_MODEL_TYPE,
                model_variant=settings.GEOMATCH_MODEL_VARIANT,
                num_gallery_images=1,  # We only have 1 landmark image
                skip_gallery_preprocessing=True,  # Skip preprocessing for landmark
            )

            # Verify the user's photo against the landmark
            logger.info(
                "Verifying image with GeoMatchAI",
                extra={
                    "latitude": message.latitude,
                    "longitude": message.longitude,
                },
            )

            is_verified, similarity_score = await verifier.verify(
                lat=message.latitude,
                lon=message.longitude,
                image_bytes=user_photo_bytes,
                skip_preprocessing=False,  # Apply preprocessing to user photo
            )

            logger.info(
                "Image verification completed",
                extra={
                    "user_id": message.user_id,
                    "landmark_id": message.landmark_id,
                    "similarity_score": similarity_score,
                    "threshold": settings.GEOMATCH_SIMILARITY_THRESHOLD,
                    "is_verified": is_verified,
                },
            )

            return UnlockVerifyResult(
                user_id=message.user_id,
                landmark_id=message.landmark_id,
                photo_url=message.photo_url,
                success=is_verified,
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
