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

    KAFKA_BOOTSTRAP_SERVERS: list[str] = Field(
        default=["kafka-0:9092", "kafka-1:9092", "kafka-2:9092"]
    )

    KAFKA_VERIFY_IMAGE_TOPIC: str = Field(default="verify-image-requests")
    KAFKA_CONSUMER_GROUP: str = Field(
        default="image-service-group", alias="KAFKA_IMAGE_CONSUMER_GROUP"
    )

    BASE_DIR: Path = Path(__file__).resolve().parent
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent


settings = Settings()
