"""Utility functions for storage operations"""

import uuid
from pathlib import Path


def generate_uuid_filename(original_filename: str) -> tuple[str, str]:
    """
    Generate a UUID-based filename while preserving the file extension.

    Args:
        original_filename: Original filename (e.g., "Снимок экрана.png")

    Returns:
        tuple: (uuid_filename, original_filename)
        - uuid_filename: UUID-based filename (e.g., "550e8400-e29b-41d4-a716-446655440000.png")
        - original_filename: Original filename for metadata

    Examples:
        >>> generate_uuid_filename("Снимок экрана 2025.png")
        ('550e8400-e29b-41d4-a716-446655440000.png', 'Снимок экрана 2025.png')
    """
    # Get file extension (lowercase)
    ext = Path(original_filename).suffix.lower()

    # Generate UUID-based filename
    uuid_filename = f"{uuid.uuid4()}{ext}"

    return uuid_filename, original_filename


def generate_storage_path(prefix: str, original_filename: str) -> tuple[str, dict]:
    """
    Generate a complete storage path with UUID filename and metadata.

    Args:
        prefix: Path prefix (e.g., "users/123" or "uploads")
        original_filename: Original filename

    Returns:
        tuple: (storage_path, metadata)
        - storage_path: Full path in storage (e.g., "users/123/uuid.png")
        - metadata: Dict with original filename for reference

    Examples:
        >>> generate_storage_path("users/123", "photo.jpg")
        ('users/123/550e8400-e29b-41d4-a716-446655440000.jpg',
         {'original_filename': 'photo.jpg'})
    """
    uuid_filename, original_filename = generate_uuid_filename(original_filename)
    storage_path = f"{prefix}/{uuid_filename}"
    metadata = {
        "original_filename": original_filename,
    }

    return storage_path, metadata


