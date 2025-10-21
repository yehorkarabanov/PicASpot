from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    PROJECT_NAME: str
    DOMAIN: str
    DEBUG: bool = Field(..., alias="BACKEND_DEBUG")
    CORS_ORIGINS: List[str] = Field(..., alias="BACKEND_CORS_ORIGINS")

    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(
        env_file=".",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


    # Email settings
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAILS_FROM_EMAIL: str
    SMTP_PORT: int
    SMTP_HOST: str
    EMAIL_FROM_NAME: str


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
