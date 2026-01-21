from fastapi import APIRouter, HTTPException, Response, UploadFile, status

from app.storage.dependencies import StorageServiceDep
from app.storage.directories import StorageDir
from app.storage.service import StorageError

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post("/upload")
async def upload_file(
    file: UploadFile,
    storage: StorageServiceDep,
    path_prefix: StorageDir = StorageDir.UPLOADS,
) -> dict:
    """
    Upload a file to storage with UUID-based filename.

    The file is stored with a UUID filename to avoid:
    - Encoding issues with non-ASCII characters
    - Filename collisions
    - Path traversal vulnerabilities

    The original filename is preserved in metadata.

    Args:
        file: File to upload
        path_prefix: Folder prefix (default: "uploads")

    Returns:
        Upload result with object_path, original_filename, and size
    """
    try:
        content = await file.read()

        result = await storage.upload_file(
            file_data=content,
            original_filename=file.filename,
            path_prefix=path_prefix,
            content_type=file.content_type or "application/octet-stream",
        )

        return {
            "message": "File uploaded successfully",
            **result,
        }
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/download/{object_path:path}")
async def download_file(
    object_path: str,
    storage: StorageServiceDep,
) -> Response:
    """
    Download a file from storage as bytes.

    Returns the file with the original filename in Content-Disposition header.

    Args:
        object_path: Path to file in storage (UUID-based)

    Returns:
        File content as bytes with appropriate headers
    """
    try:
        file_data = await storage.get_object(object_path)
        file_info = await storage.get_object_info(object_path)

        # Get original filename from metadata, fallback to UUID filename
        original_filename = file_info.get("metadata", {}).get("original_filename")
        if not original_filename:
            original_filename = object_path.split("/")[-1]

        return Response(
            content=file_data,
            media_type=file_info.get("content_type", "application/octet-stream"),
            headers={
                "Content-Disposition": f'inline; filename="{original_filename}"',
                "Cache-Control": "public, max-age=3600",
            },
        )
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.delete("/delete/{object_path:path}")
async def delete_file(
    object_path: str,
    storage: StorageServiceDep,
) -> dict:
    """
    Delete a file from storage.

    Args:
        object_path: Path to file in storage (UUID-based)

    Returns:
        Success message with deleted path
    """
    try:
        await storage.remove_object(object_path)
        return {
            "message": "File deleted successfully",
            "object_path": object_path,
        }
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/list")
async def list_objects(
    storage: StorageServiceDep,
    prefix: str = "",
    recursive: bool = True,
) -> dict:
    """
    List objects in storage.

    Args:
        prefix: Filter objects by prefix (e.g., "users/123/")
        recursive: List recursively or just immediate children

    Returns:
        List of objects with metadata
    """
    try:
        objects = await storage.list_objects(prefix=prefix, recursive=recursive)
        return {
            "objects": objects,
            "count": len(objects),
            "prefix": prefix,
        }
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/folders")
async def list_folders(
    storage: StorageServiceDep,
    prefix: str = "",
) -> dict:
    """
    List folders in storage.

    Args:
        prefix: Filter folders by prefix

    Returns:
        List of folder paths
    """
    try:
        folders = await storage.list_folders(prefix=prefix)
        return {
            "folders": folders,
            "count": len(folders),
            "prefix": prefix,
        }
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/info/{object_path:path}")
async def get_file_info(
    object_path: str,
    storage: StorageServiceDep,
) -> dict:
    """
    Get metadata about a file.

    Args:
        object_path: Path to file in storage (UUID-based)

    Returns:
        File metadata including size, content_type, and original_filename
    """
    try:
        info = await storage.get_object_info(object_path)
        return {"file_info": info}
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.head("/exists/{object_path:path}")
async def check_file_exists(
    object_path: str,
    storage: StorageServiceDep,
) -> Response:
    """
    Check if a file exists.

    Args:
        object_path: Path to file in storage (UUID-based)

    Returns:
        200 if exists, 404 if not
    """
    exists = await storage.object_exists(object_path)

    if exists:
        return Response(status_code=200)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
