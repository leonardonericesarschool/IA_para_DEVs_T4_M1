"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/pix_management_db"

    # API
    api_title: str = "Pix Key Management API"
    api_version: str = "0.1.0"
    log_level: str = "INFO"
    port: int = 8000
    host: str = "0.0.0.0"

    def __repr__(self) -> str:
        """Hide sensitive information in repr."""
        return f"{self.__class__.__name__}(***)"


settings = Settings()
