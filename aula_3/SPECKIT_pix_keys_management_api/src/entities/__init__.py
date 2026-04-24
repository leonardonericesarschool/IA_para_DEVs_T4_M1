"""Entity layer - Domain enums for Pix Keys Management"""
from enum import Enum


class PixKeyType(str, Enum):
    """Pix Key type identifiers"""
    CPF = "CPF"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    RANDOM = "RANDOM"


class PixKeyStatus(str, Enum):
    """Pix Key status states"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class PixKeyValidationStatus(str, Enum):
    """Pix Key validation status"""
    PENDING = "PENDING"
    VALID = "VALID"
    INVALID = "INVALID"


class PixKeyAuditOperation(str, Enum):
    """Audit log operation types"""
    REGISTERED = "REGISTERED"
    DEACTIVATED = "DEACTIVATED"
    REACTIVATED = "REACTIVATED"
    DELETED = "DELETED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    EDITED = "EDITED"
