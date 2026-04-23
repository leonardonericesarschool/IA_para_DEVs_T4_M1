"""FastAPI router for Pix Keys API endpoints.

This module implements the HTTP layer for Pix Key management,
following Clean Code Architecture constraints:
- Controllers depend on Use Cases (not vice versa)
- All business logic stays in Use Cases
- HTTP concerns are isolated here
- Repository injection happens in main.py
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import uuid
import logging

from src.models import RegisterPixKeyRequest, PixKeyResponse, PixKeyListResponse
from src.use_cases import RegisterPixKeyUseCase
from src.repositories import PixKeyRepository, PixKeyAuditRepository
from src.exceptions import (
    ValidationError,
    DuplicateKeyError,
    MaxKeysExceededError,
    KeyNotFoundError,
    UnauthorizedError,
)

logger = logging.getLogger(__name__)

#  Router initialization
router = APIRouter(prefix="/api/v1/pix-keys", tags=["pix-keys"])


# Dependency injection functions (to be wired in main.py)
async def get_pix_key_repository() -> PixKeyRepository:
    """Get the Pix Key repository dependency."""
    raise NotImplementedError("Repository dependency not wired")


async def get_pix_key_audit_repository() -> PixKeyAuditRepository:
    """Get the Pix Key Audit repository dependency."""
    raise NotImplementedError("Repository dependency not wired")


async def get_current_user_id() -> str:
    """Extract user_id from request context.
    
    In a real implementation, this would:
    1. Extract JWT token from Authorization header
    2. Validate and decode token
    3. Return user_id from token claims
    
    For now, returning placeholder.
    """
    # TODO: Implement JWT validation
    return str(uuid.uuid4())


@router.post(
    "/register",
    response_model=PixKeyResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Pix Key registered successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "key_id": "550e8400-e29b-41d4-a716-446655440000",
                            "user_id": "user-123",
                            "key_type": "CPF",
                            "key_value": "12345678910",  # One-time display
                            "key_value_masked": "***.***.***-10",
                            "status": "ACTIVE",
                            "alias": "My CPF",
                            "is_preferred": False,
                            "validation_status": "VALID",
                            "created_at": "2024-01-01T12:00:00Z",
                            "updated_at": "2024-01-01T12:00:00Z",
                        },
                        "message": "Pix Key registered successfully",
                        "success": True,
                    }
                }
            },
        },
        400: {
            "description": "Invalid request format or validation error",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Invalid CPF format",
                        "status_code": 400,
                        "success": False,
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized - Invalid or missing authentication token",
        },
        409: {
            "description": "Conflict - Duplicate key or invalid status transition",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Pix Key already registered for this user",
                        "status_code": 409,
                        "success": False,
                    }
                }
            },
        },
        429: {
            "description": "Too Many Requests - Maximum 5 keys per user exceeded",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Maximum 5 Pix Keys reached for this user",
                        "status_code": 429,
                        "success": False,
                    }
                }
            },
        },
    },
    summary="Register a new Pix Key",
    description="""
    Register a new Pix Key for the authenticated user.
    
    ### Key Types:
    - **CPF**: Brazilian individual taxpayer ID (11 digits)
    - **EMAIL**: Valid email address (RFC 5322)
    - **PHONE**: Brazilian phone number (11 digits, area code 11-99)
    - **RANDOM**: System-generated random key (alphanumeric)
    
    ### Important:
    - Each user can have maximum 5 Pix Keys
    - Duplicate keys are rejected
    - The plaintext key_value is shown only in this response
    - Subsequent requests will only show the masked value
    
    ### Example:
    - CPF masked: `***.***.***-10`
    - Email masked: `u***@example.com`
    - Phone masked: `(11) 9****-4321`
    """,
)
async def register_pix_key(
    request: RegisterPixKeyRequest,
    user_id: str = Depends(get_current_user_id),
    pix_key_repository: PixKeyRepository = Depends(get_pix_key_repository),
    audit_repository: PixKeyAuditRepository = Depends(get_pix_key_audit_repository),
) -> dict:
    """Register a new Pix Key for the user.
    
    Args:
        request: RegisterPixKeyRequest with key_type, key_value, alias
        user_id: Current user's ID (from JWT or session)
        pix_key_repository: Repository for Pix Key persistence
        audit_repository: Repository for audit logging
        
    Returns:
        PixKeyResponse with newly registered key (including plaintext one-time)
        
    Raises:
        HTTPException 400: Validation error (invalid format)
        HTTPException 401: Unauthorized (no valid auth)
        HTTPException 409: Conflict (duplicate or invalid state)
        HTTPException 429: Too Many Requests (limit exceeded)
    """
    try:
        logger.info(
            "registration_requested",
            extra={
                "user_id": user_id,
                "key_type": request.key_type,
            },
        )

        # Initialize use case with injected dependencies
        use_case = RegisterPixKeyUseCase(
            pix_key_repository=pix_key_repository,
            pix_key_audit_repository=audit_repository,
        )

        # Execute registration
        key, plaintext_key_value = await use_case.execute(
            user_id=user_id,
            key_type=request.key_type,
            key_value=request.key_value,
            alias=request.alias,
        )

        logger.info(
            "pix_key_registered",
            extra={
                "user_id": user_id,
                "key_id": key.key_id,
                "key_type": request.key_type,
            },
        )

        # Return response with plaintext (one-time display)
        return {
            "data": {
                **key.to_dict(),
                "key_value": plaintext_key_value,  # One-time plaintext
            },
            "message": "Pix Key registered successfully",
            "success": True,
        }

    except ValidationError as e:
        logger.warning(
            "registration_validation_error",
            extra={"user_id": user_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    except DuplicateKeyError as e:
        logger.warning(
            "registration_duplicate_error",
            extra={"user_id": user_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e

    except MaxKeysExceededError as e:
        logger.warning(
            "registration_limit_exceeded",
            extra={"user_id": user_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        ) from e

    except UnauthorizedError as e:
        logger.warning(
            "registration_unauthorized",
            extra={"user_id": user_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e

    except Exception as e:
        logger.error(
            "registration_unexpected_error",
            extra={
                "user_id": user_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration",
        ) from e
