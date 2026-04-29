"""Application configuration and settings."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration."""

    # Flask
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    TESTING = False
    FLASK_ENV = os.getenv("FLASK_ENV", "development")

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///expenses.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""

    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False


def get_config():
    """Get the appropriate configuration based on environment."""
    env = os.getenv("FLASK_ENV", "development")

    if env == "testing":
        return TestingConfig
    elif env == "production":
        return ProductionConfig
    else:
        return DevelopmentConfig
