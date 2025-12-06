import logging
from collections.abc import AsyncGenerator

from miniopy_async import Minio
from miniopy_async.error import S3Error

from app.settings import settings

logger = logging.getLogger(__name__)

# Bucket configuration
bucket_name = settings.MINIO_BUCKET_NAME


def create_minio_client() -> Minio:
    """
    Create a MinIO client instance with configured credentials.

    Returns:
        Configured MinIO client
    """
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=settings.MINIO_SECURE,
    )



async def ensure_bucket_exists() -> None:
    """
    Create MinIO bucket if it doesn't exist.

    Should be called once at application startup.

    Raises:
        S3Error: If bucket creation fails
    """
    client = create_minio_client()
    try:
        exists = await client.bucket_exists(bucket_name)
        if not exists:
            await client.make_bucket(bucket_name, location=settings.MINIO_REGION)
            logger.info(f"Created MinIO bucket: {bucket_name}")
        else:
            logger.info(f"MinIO bucket already exists: {bucket_name}")
    except S3Error as e:
        logger.error(f"Failed to create MinIO bucket: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating MinIO bucket: {e}")
        raise


async def check_minio_health() -> bool:
    """
    Check if MinIO is accessible and healthy.

    Returns:
        True if MinIO is accessible, False otherwise
    """
    client = create_minio_client()
    try:
        return await client.bucket_exists(bucket_name)
    except Exception:
        logger.exception("MinIO health check failed")
        return False


async def get_minio_client() -> AsyncGenerator[Minio, None]:
    """
    Provide MinIO client as FastAPI dependency.

    Yields MinIO client instance per request.
    Follows the same pattern as database session dependency.

    Yields:
        MinIO client instance
    """
    client = create_minio_client()
    try:
        yield client
    finally:
        # Cleanup handled by miniopy-async
        pass

