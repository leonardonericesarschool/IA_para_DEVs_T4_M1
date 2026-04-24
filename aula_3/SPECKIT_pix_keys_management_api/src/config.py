"""Application configuration using Pydantic Settings"""
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/pix_keys_db"
    database_echo: bool = False
    
    # Application
    app_name: str = "Pix Keys Management API"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # JWT/Auth
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Pix Keys Business Rules
    max_pix_keys_per_user: int = 5
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
