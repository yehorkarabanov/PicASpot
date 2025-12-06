from datetime import timedelta
from io import BytesIO

from fastapi import APIRouter, HTTPException, UploadFile, status

from app.storage.dependencies import MinioClientDep

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post("/upload-example")
async def upload_file_example(
    file: UploadFile,
    minio: MinioClientDep,
) -> dict:
    """
    Example endpoint showing how to use MinioClientDep.

    Usage in your routes:
        from app.storage.dependencies import MinioClientDep

        async def my_endpoint(minio: MinioClientDep) -> dict:
            # Use minio client with await
            await minio.put_object(bucket, path, data, length, content_type)
    """
    try:
        # Read file content
        content = await file.read()

        # Upload to MinIO using the injected client (now async!)
        object_path = f"examples/{file.filename}"
        await minio.put_object(
            bucket_name="picaspot-storage",
            object_name=object_path,
            data=BytesIO(content),
            length=len(content),
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


@router.get("/download-url-example/{object_path:path}")
async def get_download_url_example(
    object_path: str,
    minio: MinioClientDep,
) -> dict:
    """
    Example endpoint showing how to generate presigned download URLs.

    This is useful for giving users temporary access to files.
    """
    try:
        # Generate presigned URL (valid for 1 hour) - now async!
        url = await minio.presigned_get_object(
            bucket_name="picaspot-storage",
            object_name=object_path,
            expires=timedelta(hours=1),
        )

        return {
            "url": url,
            "expires_in_seconds": 3600,
            "object_path": object_path,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found or error generating URL: {str(e)}",
        )


@router.delete("/delete-example/{object_path:path}")
async def delete_file_example(
    object_path: str,
    minio: MinioClientDep,
) -> dict:
    """
    Example endpoint showing how to delete files from MinIO.
    """
    try:
        await minio.remove_object(
            bucket_name="picaspot-storage",
            object_name=object_path,
        )

        return {
            "message": "File deleted successfully",
            "object_path": object_path,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {str(e)}",
        )

