import json
import logging
from collections.abc import AsyncGenerator
from pathlib import Path

from miniopy_async import Minio
from miniopy_async.error import S3Error

from app.settings import settings

logger = logging.getLogger(__name__)


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
    Create MinIO bucket if it doesn't exist and set public read policy.

    Should be called once at application startup.

    Raises:
        S3Error: If bucket creation fails
    """
    client = create_minio_client()
    try:
        exists = await client.bucket_exists(settings.MINIO_BUCKET_NAME)
        if not exists:
            await client.make_bucket(
                settings.MINIO_BUCKET_NAME, location=settings.MINIO_REGION
            )
            logger.info(f"Created MinIO bucket: {settings.MINIO_BUCKET_NAME}")

        # Set public read policy for anonymous access through nginx
        await client.set_bucket_policy(
            settings.MINIO_BUCKET_NAME, json.dumps(settings.PUBLIC_READ_POLICY)
        )
        logger.info(f"Set public read policy on bucket: {settings.MINIO_BUCKET_NAME}")

    except S3Error as e:
        logger.error(f"Failed to create/configure MinIO bucket: {e}")
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
        return await client.bucket_exists(settings.MINIO_BUCKET_NAME)
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
        # Cleanup handled by miniopy-async :)
        await client.close_session()
        pass


async def load_default_photos(photo_paths: dict[str, Path]) -> None:
    """
    Load default photos into MinIO from specified file paths.

    Args:
        photo_paths: List of file paths to default photos
    """
    client = create_minio_client()
    try:
        for photo_name, file_path in photo_paths.items():
            object_path = f"{photo_name}.png"
            with open(file_path, "rb") as file_data:
                await client.put_object(
                    bucket_name=settings.MINIO_BUCKET_NAME,
                    object_name=photo_name,
                    data=file_data,
                    length=file_path.stat().st_size,
                    content_type="image/png",
                )
            logger.info(f"Uploaded default photo to MinIO: {object_path}")
    except S3Error as e:
        logger.error(f"Failed to upload default photos to MinIO: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error uploading default photos: {e}")
        raise
