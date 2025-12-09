import logging
import uuid
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote

from miniopy_async import Minio
from miniopy_async.error import S3Error

from .exceptions import StorageError
from .directories import StorageDir

logger = logging.getLogger(__name__)


class StorageService:
    """Service for managing MinIO object storage operations"""

    def __init__(self, client: Minio, bucket_name: str):
        """
        Initialize StorageService with MinIO client.

        Args:
            client: MinIO async client instance
            bucket_name: Name of the bucket to use
        """
        self.client = client
        self.bucket_name = bucket_name

    async def upload_file(
        self,
        file_data: bytes,
        original_filename: str,
        path_prefix: StorageDir,
        content_type: str = "application/octet-stream",
    ) -> dict:
        """
        Upload a file with UUID-based filename.

        This is the main upload method that should be used by routes.
        It automatically:
        - Generates a UUID-based filename
        - Preserves original filename in metadata
        - Stores the file

        Args:
            file_data: Raw file bytes
            original_filename: Original filename (e.g., "Снимок экрана.png")
            path_prefix: Path prefix (e.g., "users/123" or "uploads")
            content_type: MIME type of the file

        Returns:
            dict with object_path, original_filename, and size

        Example:
            result = await storage.upload_file(
                file_data=image_bytes,
                original_filename="photo.jpg",
                path_prefix=StorageDir.USERS,
                content_type="image/jpeg"
            )
            # Returns: {
            #   "object_path": "users/uuid.jpg",
            #   "original_filename": "photo.jpg",
            #   "size": 12345
            # }
        """
        # Generate UUID filename with original extension
        ext = Path(original_filename).suffix.lower()
        uuid_filename = f"{uuid.uuid4()}{ext}"
        object_path = f"{path_prefix.value}/{uuid_filename}"

        # Store original filename in metadata (URL-encoded for non-ASCII support)
        # MinIO metadata only supports US-ASCII, so we encode non-ASCII characters
        encoded_filename = quote(original_filename, safe="")
        metadata = {"original_filename": encoded_filename}

        # Upload the file
        await self.put_object(
            object_path=object_path,
            file_data=file_data,
            content_type=content_type,
            metadata=metadata,
        )

        return {
            "object_path": object_path,
            "original_filename": original_filename,
            "size": len(file_data),
        }

    async def put_object(
        self,
        object_path: str,
        file_data: bytes,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> str:
        """
        Upload a file to MinIO.

        Args:
            object_path: Path in bucket (e.g., "users/123/profile.jpg")
            file_data: Raw file bytes
            content_type: MIME type of the file
            metadata: Additional metadata to store with the file

        Returns:
            Object path in bucket

        Raises:
            StorageError: If upload fails
        """
        try:
            file_stream = BytesIO(file_data)
            await self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
                data=file_stream,
                length=len(file_data),
                content_type=content_type,
                metadata=metadata or {},
            )
            logger.info(
                f"Uploaded file: {object_path}",
                extra={"size": len(file_data), "content_type": content_type},
            )
            return object_path
        except S3Error as e:
            logger.error(f"Upload failed for {object_path}: {e}")
            raise StorageError(f"Failed to upload file: {e}") from e

    async def get_object(self, object_path: str) -> bytes:
        """
        Download a file from MinIO.

        Args:
            object_path: Path in bucket

        Returns:
            File content as bytes

        Raises:
            StorageError: If download fails or file not found
        """
        try:
            response = await self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
            )
            data = await response.read()
            response.close()

            logger.info(
                f"Downloaded file: {object_path}",
                extra={"size": len(data)},
            )
            return data
        except S3Error as e:
            logger.error(f"Download failed for {object_path}: {e}")
            raise StorageError(f"Failed to download file: {e}") from e

    async def remove_object(self, object_path: str) -> None:
        """
        Delete a file from MinIO.

        Args:
            object_path: Path in bucket

        Raises:
            StorageError: If deletion fails
        """
        try:
            await self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
            )
            logger.info(f"Deleted file: {object_path}")
        except S3Error as e:
            logger.error(f"Delete failed for {object_path}: {e}")
            raise StorageError(f"Failed to delete file: {e}") from e

    async def list_objects(
        self, prefix: str = "", recursive: bool = True
    ) -> list[dict[str, Any]]:
        """
        List objects in bucket with optional prefix filter.

        Args:
            prefix: Prefix to filter objects (e.g., "users/123/")
            recursive: If True, list all objects recursively

        Returns:
            List of objects with metadata (name, size, last_modified, etag)

        Raises:
            StorageError: If listing fails
        """
        try:
            objects = self.client.list_objects(
                bucket_name=self.bucket_name,
                prefix=prefix,
                recursive=recursive,
            )

            result = []
            async for obj in objects:
                result.append(
                    {
                        "name": obj.object_name,
                        "size": obj.size,
                        "last_modified": (
                            obj.last_modified.isoformat() if obj.last_modified else None
                        ),
                        "etag": obj.etag,
                    }
                )

            logger.info(
                f"Listed {len(result)} objects",
                extra={"prefix": prefix, "recursive": recursive},
            )
            return result
        except S3Error as e:
            logger.error(f"List objects failed: {e}")
            raise StorageError(f"Failed to list objects: {e}") from e

    async def list_folders(self, prefix: str = "") -> list[str]:
        """
        List folders (common prefixes) in bucket.

        Args:
            prefix: Prefix to filter folders

        Returns:
            List of folder paths

        Raises:
            StorageError: If listing fails
        """
        try:
            # List objects non-recursively to get folders
            objects = self.client.list_objects(
                bucket_name=self.bucket_name,
                prefix=prefix,
                recursive=False,
            )

            folders = []
            async for obj in objects:
                # Folders end with /
                if obj.is_dir:
                    folders.append(obj.object_name)

            logger.info(
                f"Listed {len(folders)} folders",
                extra={"prefix": prefix},
            )
            return folders
        except S3Error as e:
            logger.error(f"List folders failed: {e}")
            raise StorageError(f"Failed to list folders: {e}") from e

    async def object_exists(self, object_path: str) -> bool:
        """
        Check if an object exists in MinIO.

        Args:
            object_path: Path in bucket

        Returns:
            True if object exists, False otherwise
        """
        try:
            await self.client.stat_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
            )
            return True
        except S3Error:
            return False

    async def get_object_info(self, object_path: str) -> dict[str, Any]:
        """
        Get metadata about an object.

        Args:
            object_path: Path in bucket

        Returns:
            Object metadata including:
            - name: Object path
            - size: File size in bytes
            - content_type: MIME type
            - last_modified: ISO format timestamp
            - etag: ETag identifier
            - metadata: Custom metadata (including original_filename if available)

        Raises:
            StorageError: If object not found or stat operation fails
        """
        try:
            stat = await self.client.stat_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
            )

            # Decode original filename from metadata if present
            metadata = dict(stat.metadata) if stat.metadata else {}
            if "original_filename" in metadata:
                # URL-decode the filename (it was encoded to support non-ASCII)
                metadata["original_filename"] = unquote(metadata["original_filename"])

            return {
                "name": object_path,
                "size": stat.size,
                "content_type": stat.content_type,
                "last_modified": (
                    stat.last_modified.isoformat() if stat.last_modified else None
                ),
                "etag": stat.etag,
                "metadata": metadata,
            }
        except S3Error as e:
            logger.error(f"Stat object failed for {object_path}: {e}")
            raise StorageError(f"Failed to get object info: {e}") from e
