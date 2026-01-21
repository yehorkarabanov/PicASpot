import logging

from geomatchai import GeoMatchAI, MapillaryFetcher, config

from app.kafka.schemas import UnlockVerifyMessage, UnlockVerifyResult
from app.settings import settings
from app.storage import storage_service

logger = logging.getLogger(__name__)


class VerificationService:
    """Service for verifying images using GeoMatchAI."""

    def __init__(self):
        """Initialize the verification service."""
        self._started = False
        self._geomatchai_available = False
        self._verifier = None

    async def start(self) -> None:
        """Initialize GeoMatchAI configuration."""
        if self._started:
            return

        try:
            # Configure GeoMatchAI settings
            config.set_device(settings.GEOMATCH_DEVICE)
            config.set_log_level(settings.GEOMATCH_LOG_LEVEL)

            # Set Mapillary API
            if settings.MAPILLARY_API_KEY:
                config.set_mapillary_api_key(settings.MAPILLARY_API_KEY)
            else:
                logger.warning(
                    "MAPILLARY_API_KEY not set; mapillary fetcher may be limited"
                )
                raise ValueError("MAPILLARY_API_KEY is required for GeoMatchAI")
            fetcher = MapillaryFetcher(api_token=config.get_mapillary_api_key())
            self._verifier = await GeoMatchAI.create(
                fetcher=fetcher,
                threshold=settings.GEOMATCH_SIMILARITY_THRESHOLD,
                device=settings.GEOMATCH_DEVICE,
                model_type=settings.GEOMATCH_MODEL_TYPE,
                model_variant=settings.GEOMATCH_MODEL_VARIANT,
            )

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
                attempt_id=message.attempt_id,
                photo_url=message.photo_url,
                success=False,
                error="VerificationService not initialized",
            )

        try:
            # Download user photo from MinIO
            logger.info(
                "Downloading image for verification",
                extra={
                    "user_photo": message.photo_url,
                },
            )
            user_photo_bytes = await storage_service.get_object(message.photo_url)

            # Verify the user's photo against the location using Mapillary
            logger.info(
                "Verifying image with GeoMatchAI",
                extra={
                    "latitude": message.latitude,
                    "longitude": message.longitude,
                },
            )

            is_verified, similarity_score = await self._verifier.verify(
                lat=message.latitude,
                lon=message.longitude,
                image_bytes=user_photo_bytes,
                skip_preprocessing=False,  # Apply preprocessing to user photo
            )

            logger.info(
                "Image verification completed",
                extra={
                    "attempt_id": message.attempt_id,
                    "similarity_score": similarity_score,
                    "threshold": settings.GEOMATCH_SIMILARITY_THRESHOLD,
                    "is_verified": is_verified,
                },
            )

            return UnlockVerifyResult(
                attempt_id=message.attempt_id,
                photo_url=message.photo_url,
                success=is_verified,
                similarity_score=similarity_score,
            )

        except Exception as e:
            logger.error(
                f"Verification failed: {e}",
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
