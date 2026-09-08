from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "CodeSage AI"
    environment: Literal["development", "production", "test"] = "development"
    database_url: str = "sqlite+aiosqlite:///./codesage.db"
    secret_key: str = "development-only-change-me"
    cors_origins: str = "http://localhost:3000"
    app_url: str = "http://localhost:3000"
    demo_mode: bool = True
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    github_client_id: str | None = None
    github_client_secret: str | None = None
    github_app_id: str | None = None
    github_app_private_key: str | None = None
    github_webhook_secret: str | None = None

    @field_validator("github_app_private_key", mode="before")
    @classmethod
    def normalize_pem(cls, value: str | None) -> str | None:
        return value.replace("\\n", "\n") if value else value

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
