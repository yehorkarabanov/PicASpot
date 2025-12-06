import logging
from io import BytesIO

from miniopy_async import Minio
from miniopy_async.error import S3Error

from app.settings import settings

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

    async def put_object(
        self,
        object_path: str,
        file_data: bytes,
        content_type: str = "application/octet-stream",
        metadata: dict | None = None,
    ) -> str:
        """
        Upload a file to MinIO.

        Args:
            object_path: Path in bucket (e.g., "users/123/profile.jpg")
            file_data: Raw file bytes
            content_type: MIME type of the file
            metadata: Additional metadata to store with the file

        Returns:
            str: Object path in bucket

        Raises:
            Exception: If upload fails
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
            logger.info(f"Uploaded file: {object_path} ({len(file_data)} bytes)")
            return object_path
        except S3Error as e:
            logger.error(f"Upload failed for {object_path}: {e}")
            raise Exception(f"Failed to upload file: {e}")

    async def get_object(self, object_path: str) -> bytes:
        """
        Download a file from MinIO.

        Args:
            object_path: Path in bucket

        Returns:
            bytes: File content as bytes

        Raises:
            Exception: If download fails or file not found
        """
        try:
            response = await self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
            )
            data = await response.read()
            response.close()
            logger.info(f"Downloaded file: {object_path} ({len(data)} bytes)")
            return data
        except S3Error as e:
            logger.error(f"Download failed for {object_path}: {e}")
            raise Exception(f"Failed to download file: {e}")

    async def remove_object(self, object_path: str) -> None:
        """
        Delete a file from MinIO.

        Args:
            object_path: Path in bucket

        Raises:
            Exception: If deletion fails
        """
        try:
            await self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
            )
            logger.info(f"Deleted file: {object_path}")
        except S3Error as e:
            logger.error(f"Delete failed for {object_path}: {e}")
            raise Exception(f"Failed to delete file: {e}")

    async def list_objects(
        self, prefix: str = "", recursive: bool = True
    ) -> list[dict]:
        """
        List objects in bucket with optional prefix filter.

        Args:
            prefix: Prefix to filter objects (e.g., "users/123/")
            recursive: If True, list all objects recursively

        Returns:
            list[dict]: List of objects with name, size, and modified time
        """
        try:
            objects = await self.client.list_objects(
                bucket_name=self.bucket_name,
                prefix=prefix,
                recursive=recursive,
            )

            result = []
            async for obj in objects:
                result.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
                    "etag": obj.etag,
                })

            logger.info(f"Listed {len(result)} objects with prefix '{prefix}'")
            return result
        except S3Error as e:
            logger.error(f"List objects failed: {e}")
            raise Exception(f"Failed to list objects: {e}")

    async def list_folders(self, prefix: str = "") -> list[str]:
        """
        List folders (common prefixes) in bucket.

        Args:
            prefix: Prefix to filter folders

        Returns:
            list[str]: List of folder paths
        """
        try:
            # List objects non-recursively to get folders
            objects = await self.client.list_objects(
                bucket_name=self.bucket_name,
                prefix=prefix,
                recursive=False,
            )

            folders = []
            async for obj in objects:
                # Folders end with /
                if obj.is_dir:
                    folders.append(obj.object_name)

            logger.info(f"Listed {len(folders)} folders with prefix '{prefix}'")
            return folders
        except S3Error as e:
            logger.error(f"List folders failed: {e}")
            raise Exception(f"Failed to list folders: {e}")

    async def object_exists(self, object_path: str) -> bool:
        """
        Check if an object exists in MinIO.

        Args:
            object_path: Path in bucket

        Returns:
            bool: True if object exists, False otherwise
        """
        try:
            await self.client.stat_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
            )
            return True
        except S3Error:
            return False

    async def get_object_info(self, object_path: str) -> dict:
        """
        Get metadata about an object.

        Args:
            object_path: Path in bucket

        Returns:
            dict: Object metadata (size, content_type, last_modified, etc.)

        Raises:
            Exception: If object not found
        """
        try:
            stat = await self.client.stat_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
            )
            return {
                "name": object_path,
                "size": stat.size,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified.isoformat() if stat.last_modified else None,
                "etag": stat.etag,
                "metadata": stat.metadata,
            }
        except S3Error as e:
            logger.error(f"Stat object failed for {object_path}: {e}")
            raise Exception(f"Failed to get object info: {e}")

    async def put_object(
        self,
        object_path: str,
        file_data: bytes,
        content_type: str = "application/octet-stream",
        metadata: dict | None = None,
    ) -> str:
        """
        Upload a file to MinIO.

        Args:
            object_path: Path in bucket (e.g., "users/123/profile.jpg")
            file_data: Raw file bytes
            content_type: MIME type of the file
            metadata: Additional metadata to store with the file

        Returns:
            str: Object path in bucket

        Raises:
            Exception: If upload fails
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
            logger.info(f"Uploaded file: {object_path} ({len(file_data)} bytes)")
            return object_path
        except S3Error as e:
            logger.error(f"Upload failed for {object_path}: {e}")
            raise Exception(f"Failed to upload file: {e}")

    async def get_object(self, object_path: str) -> bytes:
        """
        Download a file from MinIO.

        Args:
            object_path: Path in bucket

        Returns:
            bytes: File content as bytes

        Raises:
            Exception: If download fails or file not found
        """
        try:
            response = await self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
            )
            data = await response.read()
            response.close()
            logger.info(f"Downloaded file: {object_path} ({len(data)} bytes)")
            return data
        except S3Error as e:
            logger.error(f"Download failed for {object_path}: {e}")
            raise Exception(f"Failed to download file: {e}")

    async def remove_object(self, object_path: str) -> None:
        """
        Delete a file from MinIO.

        Args:
            object_path: Path in bucket

        Raises:
            Exception: If deletion fails
        """
        try:
            await self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
            )
            logger.info(f"Deleted file: {object_path}")
        except S3Error as e:
            logger.error(f"Delete failed for {object_path}: {e}")
            raise Exception(f"Failed to delete file: {e}")

    async def list_objects(
        self, prefix: str = "", recursive: bool = True
    ) -> list[dict]:
        """
        List objects in bucket with optional prefix filter.

        Args:
            prefix: Prefix to filter objects (e.g., "users/123/")
            recursive: If True, list all objects recursively

        Returns:
            list[dict]: List of objects with name, size, and modified time
        """
        try:
            objects = await self.client.list_objects(
                bucket_name=self.bucket_name,
                prefix=prefix,
                recursive=recursive,
            )

            result = []
            async for obj in objects:
                result.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
                    "etag": obj.etag,
                })

            logger.info(f"Listed {len(result)} objects with prefix '{prefix}'")
            return result
        except S3Error as e:
            logger.error(f"List objects failed: {e}")
            raise Exception(f"Failed to list objects: {e}")

    async def list_folders(self, prefix: str = "") -> list[str]:
        """
        List folders (common prefixes) in bucket.

        Args:
            prefix: Prefix to filter folders

        Returns:
            list[str]: List of folder paths
        """
        try:
            # List objects non-recursively to get folders
            objects = await self.client.list_objects(
                bucket_name=self.bucket_name,
                prefix=prefix,
                recursive=False,
            )

            folders = []
            async for obj in objects:
                # Folders end with /
                if obj.is_dir:
                    folders.append(obj.object_name)

            logger.info(f"Listed {len(folders)} folders with prefix '{prefix}'")
            return folders
        except S3Error as e:
            logger.error(f"List folders failed: {e}")
            raise Exception(f"Failed to list folders: {e}")

    async def object_exists(self, object_path: str) -> bool:
        """
        Check if an object exists in MinIO.

        Args:
            object_path: Path in bucket

        Returns:
            bool: True if object exists, False otherwise
        """
        try:
            await self.client.stat_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
            )
            return True
        except S3Error:
            return False

    async def get_object_info(self, object_path: str) -> dict:
        """
        Get metadata about an object.

        Args:
            object_path: Path in bucket

        Returns:
            dict: Object metadata (size, content_type, last_modified, etc.)

        Raises:
            Exception: If object not found
        """
        try:
            stat = await self.client.stat_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
            )
            return {
                "name": object_path,
                "size": stat.size,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified.isoformat() if stat.last_modified else None,
                "etag": stat.etag,
                "metadata": stat.metadata,
            }
        except S3Error as e:
            logger.error(f"Stat object failed for {object_path}: {e}")
            raise Exception(f"Failed to get object info: {e}")


# Singleton instance
_storage_service: StorageService | None = None


def get_storage_service() -> StorageService:
    """Get or create the StorageService singleton"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service


