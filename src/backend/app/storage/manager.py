import logging
from collections.abc import AsyncGenerator

from miniopy_async import Minio
from miniopy_async.error import S3Error

from app.settings import settings

logger = logging.getLogger(__name__)

bucket_name = settings.MINIO_BUCKET_NAME


def create_minio_client() -> Minio:
    """Create a new MinIO client instance"""
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=settings.MINIO_SECURE,
    )


async def ensure_bucket_exists() -> None:
    """Create bucket if it doesn't exist (call once at startup)"""
    client = create_minio_client()
    try:
        bucket_exists = await client.bucket_exists(bucket_name)
        if not bucket_exists:
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


async def get_minio_client() -> AsyncGenerator[Minio, None]:
    """
    Async dependency injection for MinIO client.

    Usage in FastAPI routes:
        async def my_endpoint(minio: MinioClientDep) -> dict:
            # Use minio client with await
            await minio.put_object(...)
    """
    client = create_minio_client()
    try:
        yield client
    finally:

        pass

