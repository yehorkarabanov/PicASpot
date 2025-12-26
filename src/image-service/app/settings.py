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

    # MinIO settings
    MINIO_ENDPOINT: str = Field(default="minio1:9000")
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_SECURE: bool = Field(default=False)
    MINIO_BUCKET_NAME: str = Field(default="picaspot-storage")

    # GeoMatchAI settings
    GEOMATCH_SIMILARITY_THRESHOLD: float = Field(default=0.65)
    GEOMATCH_DEVICE: str = Field(default="auto")  # auto, cuda, or cpu
    GEOMATCH_MODEL_TYPE: str = Field(default="timm")  # timm or torchvision
    GEOMATCH_MODEL_VARIANT: str = Field(
        default="tf_efficientnet_b4.ns_jft_in1k"
    )  # TIMM model variant
    GEOMATCH_LOG_LEVEL: str = Field(default="INFO")
    MAPILLARY_API_KEY: str | None = Field(default=None)

    BASE_DIR: Path = Path(__file__).resolve().parent
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent


settings = Settings()
