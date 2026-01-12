"""
Storage module for MinIO object storage operations.

Public API:
- StorageServiceDep: Dependency for injecting StorageService into routes
- StorageService: Service class for file operations (rarely used directly)
- StorageDir: Enum for storage directory prefixes
- ensure_bucket_exists: Initialization function for startup
- check_minio_health: Health check function
- router: FastAPI router for storage endpoints
"""

from app.settings import settings

from .dependencies import StorageServiceDep, get_storage_service
from .directories import StorageDir
from .manager import check_minio_health, create_minio_client, ensure_bucket_exists
from .router import router
from .service import StorageService

# Create global storage service instance
client = create_minio_client()
storage_service = StorageService(
    client=client,
    bucket_name=settings.MINIO_BUCKET_NAME,
    public_url_base=settings.MINIO_PUBLIC_URL,
)

__all__ = [
    "StorageServiceDep",
    "StorageService",
    "StorageDir",
    "ensure_bucket_exists",
    "check_minio_health",
    "router",
    "get_storage_service",
    "storage_service",
]
