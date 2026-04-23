"""Structured logging configuration with JSON format"""
import logging
import sys
import json
from typing import Optional
from pythonjsonlogger import jsonlogger
from src.config import get_settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional context fields"""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        # Add standard fields
        log_record['timestamp'] = self.formatTime(record)
        log_record['level'] = record.levelname
        log_record['logger'] = record.name


def configure_logging(request_id: Optional[str] = None) -> None:
    """Configure structured JSON logging"""
    settings = get_settings()
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.log_level))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(logger)s %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger instance for module"""
    return logging.getLogger(name)


class RequestIdFilter(logging.Filter):
    """Add request_id to all log records"""
    
    def __init__(self, request_id: Optional[str] = None):
        super().__init__()
        self.request_id = request_id or "no-request-id"
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = self.request_id
        return True
