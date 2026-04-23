from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "Serasa Score API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = Field(default="production", pattern="^(development|staging|production)$")

    # Security
    secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Database
    database_url: str
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30

    # Redis
    redis_url: str
    score_cache_ttl_seconds: int = 86_400  # 24h
    rate_limit_window_seconds: int = 60

    # SERASA API
    serasa_api_url: str
    serasa_api_key: str
    serasa_timeout_seconds: int = 10
    serasa_max_retries: int = 3

    # Rate limiting (por IP e por API key)
    rate_limit_per_ip: int = 30        # req/min
    rate_limit_per_token: int = 100    # req/min

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY deve ter no mínimo 32 caracteres")
        return v

    @field_validator("serasa_api_key")
    @classmethod
    def validate_serasa_key(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("SERASA_API_KEY não pode ser vazia")
        return v

    def __repr__(self) -> str:
        """Nunca expõe secrets no repr (logs, debugging)."""
        return f"Settings(app={self.app_name!r}, env={self.environment!r})"


@lru_cache
def get_settings() -> Settings:
    return Settings()
