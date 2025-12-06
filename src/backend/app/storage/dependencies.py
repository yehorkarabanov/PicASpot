from typing import Annotated

from fastapi import Depends
from miniopy_async import Minio

from .manager import bucket_name, get_minio_client
from .service import StorageService


# Dependency to create StorageService from MinIO client
async def get_storage_service(
    client: Annotated[Minio, Depends(get_minio_client)]
) -> StorageService:
    """
    Create StorageService instance with MinIO client.

    Follows the same pattern as database SessionDep:
    - Manager provides the raw client (like AsyncSession)
    - Dependency wraps it in a service class

    Usage: async def my_endpoint(storage: StorageServiceDep) -> dict:
    """
    return StorageService(client=client, bucket_name=bucket_name)


# StorageServiceDep is a type alias for injecting StorageService into FastAPI route handlers.
# Usage: async def my_endpoint(storage: StorageServiceDep) -> dict:
# This provides a StorageService instance per request with MinIO client.
StorageServiceDep = Annotated[StorageService, Depends(get_storage_service)]

__all__ = ["StorageService", "StorageServiceDep"]
