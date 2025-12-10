from functools import lru_cache
from pathlib import Path
from typing import Literal, Union

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    SECRET_KEY: str
    ALGORITHM: str
    PROJECT_NAME: str
    DOMAIN: str
    DEBUG: bool = Field(..., alias="BACKEND_DEBUG")
    CORS_ORIGINS: list[str] = Field(..., alias="BACKEND_CORS_ORIGINS")
    ACCESS_TOKEN_EXPIRE_SECONDS: int

    # Service identification for logging (backend, celery_worker, flower)
    SERVICE_NAME: str = "backend"

    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str

    ADMIN_EMAIL: Union[str, Literal[False]] = Field(False, alias="ADMIN_EMAIL")
    ADMIN_PASSWORD: Union[str, Literal[False]] = Field(False, alias="ADMIN_PASSWORD")
    USER_EMAIL: Union[str, Literal[False]] = Field(False, alias="USER_EMAIL")
    USER_PASSWORD: Union[str, Literal[False]] = Field(False, alias="USER_PASSWORD")

    @property
    def DATABASE_URL(self) -> str:  # noqa: N802
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    EMAIL_VERIFY_PATH: str
    EMAIL_RESET_PASSWORD_PATH: str

    @property
    def VERIFY_EMAIL_URL(self) -> str:  # noqa: N802
        return f"{self.EMAIL_VERIFY_PATH}"

    @property
    def EMAIL_RESET_PASSWORD_URL(self) -> str:  # noqa: N802
        return f"{self.EMAIL_RESET_PASSWORD_PATH}"

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    @property
    def REDIS_URL(self) -> str:  # noqa: N802
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: list[str] = Field(
        default=["kafka-0:9092", "kafka-1:9092", "kafka-2:9092"]
    )
    KAFKA_VERIFICATION_EMAIL_TOPIC: str = Field(default="verification-email-requests")
    KAFKA_RESET_PASSWORD_EMAIL_TOPIC: str = Field(
        default="password-reset-email-requests"
    )

    # MinIO
    MINIO_ENDPOINT: str = Field(default="minio1:9000")
    MINIO_EXTERNAL_ENDPOINT: str = Field(default="localhost/dev/minio")
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_SECURE: bool = Field(default=False)
    MINIO_BUCKET_NAME: str = Field(default="picaspot-storage")
    MINIO_REGION: str = Field(default="us-east-1")

    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = Field(default=10)
    MAX_PROFILE_PICTURE_SIZE_MB: int = Field(default=5)
    MAX_LANDMARK_IMAGE_SIZE_MB: int = Field(default=10)
    MAX_UNLOCK_PHOTO_SIZE_MB: int = Field(default=15)

    # Allowed file types
    ALLOWED_IMAGE_EXTENSIONS: list[str] = Field(default=["jpg", "jpeg", "png", "webp"])
    ALLOWED_MIME_TYPES: list[str] = Field(
        default=["image/jpeg", "image/png", "image/webp"]
    )

    # Storage URL expiry settings
    STORAGE_URL_DEFAULT_EXPIRY_SECONDS: int = Field(default=3600)  # 1 hour
    STORAGE_URL_MAX_EXPIRY_SECONDS: int = Field(default=604800)  # 7 days

    # Image processing
    IMAGE_THUMBNAIL_SIZE: tuple[int, int] = Field(default=(300, 300))
    IMAGE_MAX_DIMENSION: int = Field(default=2048)
    IMAGE_QUALITY: int = Field(default=85)

    # Static files configuration
    STATIC_FILES_PATH: str = Field(default="/code/static")

    # Base URL for the application
    BASE_URL: str = Field(default="http://localhost")

    @property
    def DEFAULT_PROFILE_PICTURE_URL(self) -> str:  # noqa: N802
        """Default profile picture URL (full URL with base and API prefix)."""
        return f"{self.BASE_URL}/api/static/img/users/default_pfp.svg"

    BASE_DIR: Path = Path(__file__).resolve().parent
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
