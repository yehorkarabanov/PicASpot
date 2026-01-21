from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    SERVICE_NAME: str = Field(alias="IMAGE_SERVICE_NAME")
    PROJECT_NAME: str = Field(default="PicASpot")
    DOMAIN: str
    DEBUG: bool = Field(..., alias="BACKEND_DEBUG")

    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: list[str] = Field(
        default=["kafka-0:9092", "kafka-1:9092", "kafka-2:9092"]
    )
    KAFKA_VERIFY_IMAGE_TOPIC: str = Field(default="image-verify-requests")
    KAFKA_VERIFY_IMAGE_RESULT_TOPIC: str = Field(default="image-verify-results")
    KAFKA_CONSUMER_GROUP: str = Field(
        default="image-service-group", alias="KAFKA_IMAGE_CONSUMER_GROUP"
    )

    # MinIO
    MINIO_ENDPOINT: str = Field(default="minio1:9000")
    MINIO_EXTERNAL_ENDPOINT: str = Field(default="localhost/dev/minio")
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_SECURE: bool = Field(default=False)
    MINIO_BUCKET_NAME: str = Field(default="picaspot-storage")
    MINIO_REGION: str = Field(default="us-east-1")
    MINIO_PUBLIC_URL: str = Field(default="http://localhost/minio")

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

    @property
    def PUBLIC_READ_POLICY(self) -> dict:
        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{self.MINIO_BUCKET_NAME}/*"],
                }
            ],
        }

    # GeoMatchAI settings
    GEOMATCH_SIMILARITY_THRESHOLD: float = Field(default=0.65)
    GEOMATCH_DEVICE: str = Field(default="cuda")  # auto, cuda, or cpu
    GEOMATCH_MODEL_TYPE: str = Field(default="timm")  # timm or torchvision
    GEOMATCH_MODEL_VARIANT: str = Field(
        default="tf_efficientnet_b4.ns_jft_in1k"
    )  # TIMM model variant
    GEOMATCH_LOG_LEVEL: str = Field(default="INFO")
    MAPILLARY_API_KEY: str | None = Field(default=None)

    BASE_DIR: Path = Path(__file__).resolve().parent
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent


settings = Settings()
