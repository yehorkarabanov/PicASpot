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

from .dependencies import StorageServiceDep
from .manager import check_minio_health, ensure_bucket_exists
from .router import router
from .service import StorageService
from .directories import StorageDir

__all__ = [
    "StorageServiceDep",
    "StorageService",
    "StorageDir",
    "ensure_bucket_exists",
    "check_minio_health",
    "router",
]
