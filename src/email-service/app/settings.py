"""Settings for the email service."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Email service configuration."""

    # Service identification
    SERVICE_NAME: str = "email-service"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, alias="BACKEND_DEBUG")

    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: list[str] = Field(
        default=["kafka-0:9092", "kafka-1:9092", "kafka-2:9092"]
    )
    KAFKA_EMAIL_TOPIC: str = Field(default="email-events")
    KAFKA_CONSUMER_GROUP: str = Field(default="email-service-group")
    KAFKA_AUTO_OFFSET_RESET: str = Field(default="earliest")
    KAFKA_MAX_POLL_RECORDS: int = Field(default=100)
    KAFKA_SESSION_TIMEOUT_MS: int = Field(default=30000)
    KAFKA_HEARTBEAT_INTERVAL_MS: int = Field(default=10000)
    KAFKA_MAX_POLL_INTERVAL_MS: int = Field(default=300000)

    # Email/SMTP settings
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_PORT: int
    SMTP_HOST: str
    EMAIL_FROM_NAME: str
    PROJECT_NAME: str = Field(default="PicASpot")

    # Email retry settings
    EMAIL_MAX_RETRIES: int = Field(default=3)
    EMAIL_RETRY_DELAY_SECONDS: int = Field(default=5)

    # Paths
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent)

    @property
    def TEMPLATE_FOLDER(self) -> Path:
        """Returns the path to email templates."""
        return self.BASE_DIR / "handlers" / "templates"

    @property
    def KAFKA_BOOTSTRAP_SERVERS_STRING(self) -> str:
        """Returns Kafka bootstrap servers as comma-separated string."""
        return ",".join(self.KAFKA_BOOTSTRAP_SERVERS)

    model_config = SettingsConfigDict(
        env_file="core",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
