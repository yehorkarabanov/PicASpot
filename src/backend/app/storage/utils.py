"""Utility functions for storage operations"""

from urllib.parse import urlparse, urlunparse

from app.settings import settings


def fix_presigned_url(internal_url: str) -> str:
    """
    Replace internal MinIO endpoint with external NGINX proxy endpoint in presigned URLs.

    This is necessary because MinIO generates URLs using the internal Docker
    hostname (minio1:9000) which is not accessible from outside the container.

    The function converts:
        http://minio1:9000/bucket/file?signature=...
    To:
        http://localhost/storage/bucket/file?signature=...

    This routes through NGINX proxy which handles load balancing and is accessible externally.

    Args:
        internal_url: URL with internal endpoint (e.g., http://minio1:9000/...)

    Returns:
        URL with external NGINX proxy endpoint (e.g., http://localhost/storage/...)
    """
    parsed = urlparse(internal_url)

    # Get external endpoint from settings (e.g., "localhost" or "yourdomain.com")
    external_host = settings.MINIO_EXTERNAL_ENDPOINT.split(':')[0]  # Remove port if present

    # Determine protocol (http or https)
    protocol = "https" if settings.MINIO_SECURE else "http"

    # Add /storage prefix to path for NGINX routing
    new_path = f"/storage{parsed.path}"

    # Reconstruct URL with external endpoint and NGINX proxy path
    external_url = str(urlunparse((
        protocol,
        external_host,  # Use external host without port (NGINX handles standard ports)
        new_path,
        parsed.params,
        parsed.query,
        parsed.fragment
    )))

    return external_url

