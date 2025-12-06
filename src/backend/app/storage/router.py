from fastapi import APIRouter, HTTPException, Response, UploadFile, status

from app.storage.dependencies import StorageServiceDep

example_router = APIRouter(prefix="/storage", tags=["storage"])


@example_router.post("/upload")
async def upload_file(
    file: UploadFile,
    storage: StorageServiceDep,
    path_prefix: str = "uploads",
) -> dict:
    """
    Upload a file to storage.

    Args:
        file: File to upload
        path_prefix: Folder prefix (default: "uploads")

    Returns:
        dict with object_path and size
    """
    try:
        # Read file content
        content = await file.read()

        # Upload to MinIO
        object_path = f"{path_prefix}/{file.filename}"
        await storage.put_object(
            object_path=object_path,
            file_data=content,
            content_type=file.content_type or "application/octet-stream",
        )

        return {
            "message": "File uploaded successfully",
            "object_path": object_path,
            "size": len(content),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )


@example_router.get("/download/{object_path:path}")
async def download_file(
    object_path: str,
    storage: StorageServiceDep,
) -> Response:
    """
    Download a file from storage as bytes.

    Args:
        object_path: Path to file in storage

    Returns:
        File content as bytes with appropriate content-type header
    """
    try:
        # Get file bytes
        file_data = await storage.get_object(object_path)

        # Get file info to determine content type
        file_info = await storage.get_object_info(object_path)

        # Return file as response with appropriate headers
        return Response(
            content=file_data,
            media_type=file_info.get("content_type", "application/octet-stream"),
            headers={
                "Content-Disposition": f'inline; filename="{object_path.split("/")[-1]}"',
                "Cache-Control": "public, max-age=3600",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {str(e)}",
        )


@example_router.delete("/delete/{object_path:path}")
async def delete_file(
    object_path: str,
    storage: StorageServiceDep,
) -> dict:
    """
    Delete a file from storage.

    Args:
        object_path: Path to file in storage

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


@example_router.get("/list")
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"List failed: {str(e)}",
        )


@example_router.get("/folders")
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


@example_router.get("/info/{object_path:path}")
async def get_file_info(
    object_path: str,
    storage: StorageServiceDep,
) -> dict:
    """
    Get metadata about a file.

    Args:
        object_path: Path to file in storage

    Returns:
        File metadata (size, content_type, last_modified, etc.)
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


@example_router.head("/exists/{object_path:path}")
async def check_file_exists(
    object_path: str,
    storage: StorageServiceDep,
) -> Response:
    """
    Check if a file exists.

    Args:
        object_path: Path to file in storage

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


