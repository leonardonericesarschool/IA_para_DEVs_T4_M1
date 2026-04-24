"""Structured logging configuration."""
import logging
import json
from pythonjsonlogger import jsonlogger

from src.config import settings


def setup_logging() -> None:
    """Configure structured JSON logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)

    # JSON formatter
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt="%(timestamp)s %(level)s %(name)s %(message)s",
        timestamp=True,
    )
    logHandler.setFormatter(formatter)
    root_logger.addHandler(logHandler)

    # Suppress verbose SQLAlchemy logging
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
