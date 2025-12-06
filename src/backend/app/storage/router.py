from fastapi import APIRouter, HTTPException, Response, UploadFile, status

from app.storage.dependencies import StorageServiceDep

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post("/upload")
async def upload_file(
    file: UploadFile,
    storage: StorageServiceDep,
    path_prefix: str = "uploads",
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
        dict with object_path, original_filename, and size
    """
    try:
        # Read file content
        content = await file.read()

        # Upload using StorageService (handles UUID generation internally)
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )


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
        File content as bytes with appropriate content-type header
    """
    try:
        # Get file bytes
        file_data = await storage.get_object(object_path)

        # Get file info to determine content type and original filename
        file_info = await storage.get_object_info(object_path)

        # Get original filename from metadata, fallback to object path filename
        original_filename = file_info.get("metadata", {}).get("original_filename")
        if not original_filename:
            # Fallback to UUID filename if metadata not available
            original_filename = object_path.split("/")[-1]

        # Return file as response with appropriate headers
        return Response(
            content=file_data,
            media_type=file_info.get("content_type", "application/octet-stream"),
            headers={
                "Content-Disposition": f'inline; filename="{original_filename}"',
                "Cache-Control": "public, max-age=3600",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {str(e)}",
        )


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
        Success message
    """
    try:
        await storage.remove_object(object_path)

        return {
            "message": "File deleted successfully",
            "object_path": object_path,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {str(e)}",
        )


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
        List of objects with metadata including original filenames
    """
    try:
        objects = await storage.list_objects(prefix=prefix, recursive=recursive)

        return {
            "objects": objects,
            "count": len(objects),
            "prefix": prefix,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"List failed: {str(e)}",
        )


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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"List folders failed: {str(e)}",
        )


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
        File metadata (size, content_type, last_modified, original_filename, etc.)
    """
    try:
        info = await storage.get_object_info(object_path)

        return {
            "file_info": info,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {str(e)}",
        )


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



