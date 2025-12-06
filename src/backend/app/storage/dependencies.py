from typing import Annotated

from fastapi import Depends
from miniopy_async import Minio

from .manager import get_minio_client

# MinioClientDep is a type alias for injecting an async MinIO client into FastAPI route handlers.
# Usage: async def my_endpoint(minio: MinioClientDep) -> dict:
# This provides an async MinIO client instance per request for object storage operations.
# All operations must be awaited: await minio.put_object(...)
MinioClientDep = Annotated[Minio, Depends(get_minio_client)]

