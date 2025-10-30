from functools import lru_cache
from pathlib import Path
from typing import Literal, Union

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    PROJECT_NAME: str
    DOMAIN: str
    DEBUG: bool = Field(..., alias="BACKEND_DEBUG")
    CORS_ORIGINS: list[str] = Field(..., alias="BACKEND_CORS_ORIGINS")
    ACCESS_TOKEN_EXPIRE_SECONDS: int

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

    BASE_DIR: Path = Path(__file__).resolve().parent
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
