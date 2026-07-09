"""Centralized application settings loaded from environment variables.

Using pydantic's BaseSettings keeps configuration validated, typed, and
easy to override per environment (local, staging, production) without
touching application code.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the PulseBoard API."""

    # General
    app_name: str = "PulseBoard API"
    environment: str = "development"
    debug: bool = False

    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8  # 8 hours

    # Database
    database_url: str = "postgresql+psycopg2://pulseboard:pulseboard@localhost:5432/pulseboard"

    # CORS
    allowed_origins: list[str] = ["http://localhost:5173"]

    # Pagination
    default_page_size: int = 25
    max_page_size: int = 200

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance so env parsing happens once."""
    return Settings()
