import logging
import uuid
from datetime import timedelta
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote

from miniopy_async import Minio
from miniopy_async.error import S3Error

from app.settings import settings

from .directories import StorageDir
from .exceptions import StorageError

logger = logging.getLogger(__name__)


class StorageService:
    """Service for managing MinIO object storage operations"""

    def __init__(
        self, client: Minio, bucket_name: str, public_url_base: str | None = None
    ):
        """
        Initialize StorageService with MinIO client.

        Args:
            client: MinIO async client instance
            bucket_name: Name of the bucket to use
            public_url_base: Base URL for public access (e.g., "http://localhost/minio")
        """
        self.client = client
        self.bucket_name = bucket_name
        self.public_url_base = public_url_base
        self.default_url_expiry = timedelta(
            seconds=settings.STORAGE_URL_DEFAULT_EXPIRY_SECONDS
        )
        self.max_url_expiry = timedelta(seconds=settings.STORAGE_URL_MAX_EXPIRY_SECONDS)

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

        # Generate the public URL for the uploaded file
        public_url = (
            self.get_public_url(object_path) if self.public_url_base else object_path
        )

        return {
            "object_path": object_path,
            "public_url": public_url,
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

    async def get_object_url(
        self,
        object_path: str,
        expires: timedelta | None = None,
    ) -> str:
        """
        Generate a presigned URL for accessing an object.

        This creates a temporary URL that allows direct access to the file
        without requiring authentication. Useful for serving images, downloads, etc.

        Args:
            object_path: Path in bucket (e.g., "users/123/profile.jpg")
            expires: URL expiration time (default: 1 hour, max: 7 days)

        Returns:
            Presigned URL string

        Raises:
            StorageError: If URL generation fails
            ValueError: If expiration time exceeds maximum

        Example:
            url = await storage.get_object_url("users/123/photo.jpg")
            # Returns: "https://minio.example.com/bucket/users/123/photo.jpg?..."
        """
        try:
            # Use default expiry if not specified
            if expires is None:
                expires = self.default_url_expiry

            # Validate expiration time
            if expires > self.max_url_expiry:
                raise ValueError(
                    f"URL expiration cannot exceed {self.max_url_expiry.days} days"
                )

            # Generate presigned URL
            url = await self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
                expires=expires,
            )

            logger.info(
                f"Generated presigned URL for {object_path}",
                extra={"expires_seconds": expires.total_seconds()},
            )
            return url

        except S3Error as e:
            logger.error(f"Failed to generate URL for {object_path}: {e}")
            raise StorageError(f"Failed to generate object URL: {e}") from e

    async def get_image_url(
        self,
        object_path: str,
        expires: timedelta | None = None,
    ) -> str:
        """
        Generate a presigned URL for accessing an image.

        This is a convenience method that calls get_object_url but is more
        semantically clear when working with images.

        Args:
            object_path: Path to image in bucket (e.g., "users/123/profile.jpg")
            expires: URL expiration time (default: 1 hour, max: 7 days)

        Returns:
            Presigned URL string

        Raises:
            StorageError: If URL generation fails
            ValueError: If expiration time exceeds maximum

        Example:
            url = await storage.get_image_url("users/123/photo.jpg")
            # Use URL in frontend: <img src="{url}" />
        """
        return await self.get_object_url(object_path, expires)

    def get_public_url(self, object_path: str) -> str:
        """
        Generate a constant public URL for accessing an object through nginx proxy.

        This creates a permanent URL that routes through nginx to MinIO.
        The URL does not expire and is suitable for public image access.

        Args:
            object_path: Path in bucket (e.g., "users/123/profile.jpg")

        Returns:
            Public URL string in format: {public_url_base}/{bucket_name}/{object_path}

        Raises:
            StorageError: If public URL base is not configured

        Example:
            url = storage.get_public_url("users/123/photo.jpg")
            # Returns: "http://localhost/minio/picaspot-storage/users/123/photo.jpg"
        """
        if not self.public_url_base:
            raise StorageError("Public URL base is not configured")

        # Construct the public URL: base/bucket/object_path
        url = f"{self.public_url_base.rstrip('/')}/{self.bucket_name}/{object_path}"

        logger.debug(
            f"Generated public URL for {object_path}",
            extra={"url": url},
        )
        return url

    def get_public_image_url(self, object_path: str) -> str:
        """
        Generate a constant public URL for accessing an image through nginx proxy.

        This is a convenience method that calls get_public_url but is more
        semantically clear when working with images.

        Args:
            object_path: Path to image in bucket (e.g., "users/123/profile.jpg")

        Returns:
            Public URL string

        Example:
            url = storage.get_public_image_url("users/123/photo.jpg")
            # Returns: "http://localhost/minio/picaspot-storage/users/123/photo.jpg"
        """
        return self.get_public_url(object_path)

    def extract_object_path(self, public_url: str) -> str | None:
        """
        Extract the object path from a public URL.

        This is useful when you need to delete or modify an object but only have
        the public URL stored in the database.

        Args:
            public_url: Full public URL (e.g., "http://localhost/minio/bucket/path/file.jpg")

        Returns:
            Object path (e.g., "path/file.jpg") or None if URL format is invalid

        Example:
            path = storage.extract_object_path("http://localhost/minio/picaspot-storage/users/123/photo.jpg")
            # Returns: "users/123/photo.jpg"
        """
        if not public_url or not self.public_url_base:
            return None

        # Expected format: {public_url_base}/{bucket_name}/{object_path}
        prefix = f"{self.public_url_base.rstrip('/')}/{self.bucket_name}/"
        if public_url.startswith(prefix):
            return public_url[len(prefix) :]

        return None

    def get_multiple_public_image_urls(
        self,
        object_paths: list[str],
    ) -> dict[str, str]:
        """
        Generate public URLs for multiple images at once.

        Args:
            object_paths: List of object paths

        Returns:
            Dictionary mapping object_path to public URL
            Failed URLs will have None as value

        Example:
            paths = ["users/123/photo1.jpg", "users/123/photo2.jpg"]
            urls = storage.get_multiple_public_image_urls(paths)
            # Returns: {
            #   "users/123/photo1.jpg": "http://localhost/minio/...",
            #   "users/123/photo2.jpg": "http://localhost/minio/...",
            # }
        """
        result = {}

        for object_path in object_paths:
            try:
                url = self.get_public_image_url(object_path)
                result[object_path] = url
            except StorageError as e:
                logger.error(f"Failed to generate public URL for {object_path}: {e}")
                result[object_path] = None

        return result

    async def get_multiple_image_urls(
        self,
        object_paths: list[str],
        expires: timedelta | None = None,
    ) -> dict[str, str]:
        """
        Generate presigned URLs for multiple images at once.

        Args:
            object_paths: List of object paths
            expires: URL expiration time (default: 1 hour, max: 7 days)

        Returns:
            Dictionary mapping object_path to presigned URL
            Failed URLs will have None as value

        Example:
            paths = ["users/123/photo1.jpg", "users/123/photo2.jpg"]
            urls = await storage.get_multiple_image_urls(paths)
            # Returns: {
            #   "users/123/photo1.jpg": "https://...",
            #   "users/123/photo2.jpg": "https://...",
            # }
        """
        result = {}

        for object_path in object_paths:
            try:
                url = await self.get_image_url(object_path, expires)
                result[object_path] = url
            except (StorageError, ValueError) as e:
                logger.error(f"Failed to generate URL for {object_path}: {e}")
                result[object_path] = None

        return result

    async def get_upload_url(
        self,
        object_path: str,
        expires: timedelta | None = None,
    ) -> str:
        """
        Generate a presigned URL for uploading an object.

        This allows clients to upload directly to MinIO without going through
        the backend, useful for large file uploads.

        Args:
            object_path: Destination path in bucket
            expires: URL expiration time (default: 1 hour, max: 7 days)

        Returns:
            Presigned upload URL string

        Raises:
            StorageError: If URL generation fails
            ValueError: If expiration time exceeds maximum

        Example:
            url = await storage.get_upload_url("users/123/upload.jpg")
            # Client can PUT to this URL directly
        """
        try:
            # Use default expiry if not specified
            if expires is None:
                expires = self.default_url_expiry

            # Validate expiration time
            if expires > self.max_url_expiry:
                raise ValueError(
                    f"URL expiration cannot exceed {self.max_url_expiry.days} days"
                )

            # Generate presigned upload URL
            url = await self.client.presigned_put_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
                expires=expires,
            )

            logger.info(
                f"Generated presigned upload URL for {object_path}",
                extra={"expires_seconds": expires.total_seconds()},
            )
            return url

        except S3Error as e:
            logger.error(f"Failed to generate upload URL for {object_path}: {e}")
            raise StorageError(f"Failed to generate upload URL: {e}") from e

    async def start(self) -> None:
        """Initialize storage service by ensuring bucket exists."""
        from .manager import ensure_bucket_exists

        await ensure_bucket_exists()

    async def stop(self) -> None:
        """Cleanup storage service resources."""
        await self.client.close_session()

    async def health_check(self) -> bool:
        """Check if storage service is healthy."""
        from .manager import check_minio_health

        return await check_minio_health()
