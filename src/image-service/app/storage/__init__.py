"""
Storage module for MinIO object storage operations in image-service.
"""

from .service import StorageService, storage_service

__all__ = [
    "StorageService",
    "storage_service",
]
