"""Custom exceptions for Pix Keys Management application"""
from typing import Any, Dict, Optional


class PixKeysException(Exception):
    """Base exception for all Pix Keys errors"""
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


# Domain Exceptions (Business Logic Violations)
class DomainException(PixKeysException):
    """Exception for business rule violations in the domain layer"""
    pass


class ValidationError(DomainException):
    """Invalid input data format or content"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class DuplicateKeyError(DomainException):
    """Key already registered for user"""
    def __init__(self, key_id: Optional[str] = None, status: Optional[str] = None):
        details = {}
        if key_id:
            details["key_id"] = key_id
        if status:
            details["status"] = status
        super().__init__(
            message="This key is already registered on your account",
            code="KEY_ALREADY_EXISTS",
            status_code=409,
            details=details
        )


class MaxKeysExceededError(DomainException):
    """User exceeded maximum keys limit"""
    def __init__(self, max_allowed: int = 5, current_count: int = 5):
        super().__init__(
            message=f"You have reached the maximum number of Pix Keys ({max_allowed}). "
                   f"Delete or deactivate unused keys to register new ones.",
            code="MAX_KEYS_EXCEEDED",
            status_code=429,
            details={"max_allowed": max_allowed, "current_count": current_count}
        )


# Application Exceptions (Use Case/Domain Logic)
class ApplicationException(PixKeysException):
    """Exception for use case or application logic failures"""
    pass


class KeyNotFoundError(ApplicationException):
    """Requested key does not exist"""
    def __init__(self):
        super().__init__(
            message="Pix Key not found",
            code="KEY_NOT_FOUND",
            status_code=404
        )


class UnauthorizedError(ApplicationException):
    """User not authorized to perform action"""
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=403
        )


class InvalidFilterError(ApplicationException):
    """Invalid filter parameter provided"""
    def __init__(self, message: str = "Invalid filter parameter"):
        super().__init__(
            message=message,
            code="INVALID_FILTER",
            status_code=400
        )


class InvalidStatusTransitionError(ApplicationException):
    """Invalid status state transition"""
    def __init__(self, current_status: str, attempted_status: str):
        super().__init__(
            message=f"Cannot transition from {current_status} to {attempted_status}",
            code="INVALID_STATUS_TRANSITION",
            status_code=409,
            details={"current_status": current_status, "attempted_status": attempted_status}
        )


class CannotDeleteActiveKeyError(ApplicationException):
    """Cannot delete an active key"""
    def __init__(self):
        super().__init__(
            message="Only inactive keys can be deleted. Please deactivate the key first.",
            code="CANNOT_DELETE_ACTIVE_KEY",
            status_code=409
        )


# Infrastructure Exceptions
class InfrastructureException(PixKeysException):
    """Exception for infrastructure/external system failures"""
    pass


class DatabaseError(InfrastructureException):
    """Database operation failed"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500
        )


class ExternalServiceError(InfrastructureException):
    """External service (e.g., Pix network) error"""
    def __init__(self, service: str = "External Service", message: str = "Service unavailable"):
        super().__init__(
            message=f"{service}: {message}",
            code="EXTERNAL_SERVICE_ERROR",
            status_code=503
        )
