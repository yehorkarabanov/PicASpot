"""Manager for MinIO client creation and initialization"""

import logging
from collections.abc import AsyncGenerator

from miniopy_async import Minio
from miniopy_async.error import S3Error

from app.settings import settings

logger = logging.getLogger(__name__)


# MinIO client configuration
def create_minio_client() -> Minio:
    """Create a MinIO client instance"""
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=settings.MINIO_SECURE,
    )


# Bucket name
bucket_name = settings.MINIO_BUCKET_NAME


async def ensure_bucket_exists() -> None:
    """Create bucket if it doesn't exist (call once at startup)"""
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
    """Check if MinIO is accessible"""
    client = create_minio_client()
    try:
        return await client.bucket_exists(bucket_name)
    except Exception:
        logger.exception("MinIO health check failed")
        return False


# Dependency for FastAPI (similar to get_async_session pattern)
async def get_minio_client() -> AsyncGenerator[Minio, None]:
    """
    Dependency for providing MinIO client to routes.

    Yields a MinIO client instance per request.
    Similar to database session pattern.
    """
    client = create_minio_client()
    try:
        yield client
    finally:
        # Cleanup if needed (miniopy-async handles connection cleanup)
        pass

