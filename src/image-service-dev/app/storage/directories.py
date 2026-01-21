from enum import Enum


class StorageDir(Enum):
    """Enum for MinIO storage folder prefixes."""

    USERS = "users"
    UPLOADS = "uploads"
    LANDMARKS = "landmarks"
    UNLOCKS = "unlocks"
    AREAS = "areas"
