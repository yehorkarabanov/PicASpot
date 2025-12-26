import logging
from urllib.parse import urlparse

from miniopy_async import Minio
from miniopy_async.error import S3Error

from app.settings import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for downloading files from MinIO storage."""

    def __init__(self):
        """Initialize StorageService with MinIO client."""
        self.client: Minio | None = None
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._started = False

    async def start(self) -> None:
        """Initialize the MinIO client."""
        if self._started:
            return

        try:
            self.client = Minio(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ROOT_USER,
                secret_key=settings.MINIO_ROOT_PASSWORD,
                secure=settings.MINIO_SECURE,
            )
            self._started = True
            logger.info(
                "MinIO client initialized",
                extra={"endpoint": settings.MINIO_ENDPOINT},
            )
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            raise

    async def stop(self) -> None:
        """Cleanup MinIO client resources."""
        self._started = False
        self.client = None
        logger.info("MinIO client stopped")

    def extract_object_path(self, url: str) -> str:
        """
        Extract object path from a MinIO URL.

        Handles URLs like:
        - http://localhost/minio/picaspot-storage/unlocks/uuid.jpg
        - unlocks/uuid.jpg (direct path)

        Args:
            url: Full URL or object path

        Returns:
            Object path in bucket (e.g., "unlocks/uuid.jpg")
        """
        if url.startswith("http://") or url.startswith("https://"):
            parsed = urlparse(url)
            path = parsed.path

            # Remove leading slash
            if path.startswith("/"):
                path = path[1:]

            # Check if path starts with bucket name
            if path.startswith(f"{self.bucket_name}/"):
                path = path[len(self.bucket_name) + 1 :]

            # Check for minio prefix pattern: minio/bucket/path
            parts = path.split("/")
            if len(parts) > 2 and parts[0] == "minio":
                # Skip 'minio' and bucket name
                path = "/".join(parts[2:])

            return path
        return url

    async def get_object(self, object_path: str) -> bytes:
        """
        Download a file from MinIO.

        Args:
            object_path: Path in bucket or full URL

        Returns:
            File content as bytes

        Raises:
            Exception: If download fails or file not found
        """
        if not self.client or not self._started:
            raise RuntimeError("StorageService not started")

        # Extract object path from URL if needed
        path = self.extract_object_path(object_path)

        try:
            response = await self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=path,
            )
            data = await response.read()
            response.close()

            logger.info(
                f"Downloaded file: {path}",
                extra={"size": len(data)},
            )
            return data
        except S3Error as e:
            logger.error(f"Download failed for {path}: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if MinIO connection is healthy."""
        if not self.client or not self._started:
            return False
        try:
            await self.client.bucket_exists(self.bucket_name)
            return True
        except Exception as e:
            logger.warning(f"MinIO health check failed: {e}")
            return False


# Global singleton instance
storage_service = StorageService()
