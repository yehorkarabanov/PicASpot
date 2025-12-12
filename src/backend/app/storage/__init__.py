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
from .directories import StorageDir
from .manager import check_minio_health, ensure_bucket_exists, load_default_photos
from .router import router
from .service import StorageService

__all__ = [
    "StorageServiceDep",
    "StorageService",
    "StorageDir",
    "ensure_bucket_exists",
    "check_minio_health",
    "router",
    "load_default_photos",
]
