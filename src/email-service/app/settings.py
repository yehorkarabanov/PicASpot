from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    PROJECT_NAME: str
    DOMAIN: str
    DEBUG: bool = Field(..., alias="BACKEND_DEBUG")

    # Email settings
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAILS_FROM_EMAIL: str
    SMTP_PORT: int
    SMTP_HOST: str
    EMAIL_FROM_NAME: str

    KAFKA_BOOTSTRAP_SERVERS: list[str] = Field(
        default=["kafka-0:9092", "kafka-1:9092", "kafka-2:9092"]
    )
    KAFKA_VERIFICATION_EMAIL_TOPIC: str = Field(default="verification-email-requests")
    KAFKA_RESET_PASSWORD_EMAIL_TOPIC: str = Field(
        default="password-reset-email-requests"
    )
