from typing import Annotated

from fastapi import Depends
from miniopy_async import Minio

from app.settings import settings

from .manager import bucket_name, get_minio_client
from .service import StorageService


async def get_storage_service(
    client: Annotated[Minio, Depends(get_minio_client)],
) -> StorageService:
    """
    Create StorageService instance with MinIO client.

    Args:
        client: MinIO client from dependency

    Returns:
        Configured StorageService instance

    Usage:
        async def my_endpoint(storage: StorageServiceDep) -> dict:
            result = await storage.upload_file(...)
    """
    return StorageService(
        client=client,
        bucket_name=bucket_name,
        public_url_base=settings.MINIO_PUBLIC_URL,
    )


# Type alias for injecting StorageService into FastAPI route handlers
StorageServiceDep = Annotated[StorageService, Depends(get_storage_service)]

__all__ = ["StorageService", "StorageServiceDep"]
