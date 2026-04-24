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
    """Register a new Pix Key for the authenticated user.
    
    This endpoint allows users to register a new Pix Key (CPF, EMAIL, PHONE, or RANDOM)
    and receive a one-time display of the plaintext value. After registration,
    the key is stored securely using hash and only the masked value is displayed.
    
    **Key Features:**
    - One-time display of plaintext key during registration
    - Automatic masking for subsequent requests
    - Secure SHA-256 hashing for storage
    - Duplicate detection and max 5 keys per user limit
    - Comprehensive validation for each key type
    - Automatic audit trail creation
    
    **Request Body Example:**
    ```json
    {
        "key_type": "CPF",
        "key_value": "12345678910",
        "alias": "My CPF"
    }
    ```
    
    **Response Example (201 Created):**
    ```json
    {
        "data": {
            "key_id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "user-123",
            "key_type": "CPF",
            "key_value": "12345678910",
            "key_value_masked": "***.***.***-10",
            "status": "ACTIVE",
            "alias": "My CPF",
            "is_preferred": false,
            "validation_status": "VALID",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z"
        },
        "message": "Pix Key registered successfully",
        "success": true
    }
    ```
    
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


@router.get(
    "/list",
    status_code=status.HTTP_200_OK,
    summary="List user's Pix Keys",
    description="""
    Retrieve a paginated list of all registered Pix Keys for the authenticated user.
    
    ### Features:
    - Filter by status (ACTIVE, INACTIVE)
    - Filter by key type (CPF, EMAIL, PHONE, RANDOM)
    - Sort by created_at (default), updated_at, or key_type
    - Pagination with configurable page size
    
    ### Example:
    ```
    GET /api/v1/pix-keys/list?status=ACTIVE&sort_by=created_at&page=1&limit=10
    ```
    """,
)
async def list_pix_keys(
    user_id: str = Depends(get_current_user_id),
    pix_key_repository: PixKeyRepository = Depends(get_pix_key_repository),
    status: str = None,
    key_type: str = None,
    sort_by: str = "created_at",
    page: int = 1,
    limit: int = 10,
) -> dict:
    """List all Pix Keys for the user with filtering and pagination.
    
    Args:
        user_id: Current user's ID (from auth)
        pix_key_repository: Repository for data access
        status: Filter by status (ACTIVE, INACTIVE, None for all)
        key_type: Filter by type (CPF, EMAIL, PHONE, RANDOM, None for all)
        sort_by: Sort field (created_at, updated_at, key_type)
        page: Page number (1-indexed)
        limit: Items per page (max 100)
        
    Returns:
        Dictionary with keys list and pagination info
        
    Raises:
        HTTPException 400: Invalid filter parameter
        HTTPException 401: Unauthorized
    """
    try:
        from src.use_cases.view_pix_keys import ViewPixKeysUseCase
        from src.exceptions import InvalidFilterError
        
        # Limit page size to 100 for safety
        limit = min(limit, 100)
        
        logger.info(
            "list_pix_keys_requested",
            extra={
                "user_id": user_id,
                "status": status,
                "key_type": key_type,
                "sort_by": sort_by,
                "page": page,
                "limit": limit,
            },
        )
        
        # Create use case with injected repository
        use_case = ViewPixKeysUseCase(pix_key_repository=pix_key_repository)
        
        # Execute use case
        result = await use_case.execute(
            user_id=user_id,
            status=status,
            key_type=key_type,
            sort_by=sort_by,
            page=page,
            limit=limit,
        )
        
        logger.info(
            "pix_keys_listed",
            extra={
                "user_id": user_id,
                "count": len(result["keys"]),
                "total": result["pagination"]["total"],
            },
        )
        
        return {
            "data": result["keys"],
            "pagination": result["pagination"],
            "message": f"Found {result['pagination']['total']} Pix Keys",
            "success": True,
        }
        
    except InvalidFilterError as e:
        logger.warning(
            "list_invalid_filter",
            extra={"user_id": user_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    
    except Exception as e:
        logger.error(
            "list_unexpected_error",
            extra={
                "user_id": user_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while listing keys",
        ) from e


@router.get(
    "/{key_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Pix Key details",
    description="Retrieve details of a specific Pix Key by ID (masked value only)",
)
async def get_pix_key(
    key_id: str,
    user_id: str = Depends(get_current_user_id),
    pix_key_repository: PixKeyRepository = Depends(get_pix_key_repository),
) -> dict:
    """Get details of a specific Pix Key.
    
    Args:
        key_id: ID of the Pix Key to retrieve
        user_id: Current user's ID (from auth)
        pix_key_repository: Repository for data access
        
    Returns:
        PixKeyResponse with key details
        
    Raises:
        HTTPException 404: Key not found
        HTTPException 403: User not authorized to access this key
    """
    try:
        logger.info(
            "get_pix_key_requested",
            extra={"user_id": user_id, "key_id": key_id},
        )
        
        # Get key from repository
        key = await pix_key_repository.get_by_id(key_id)
        
        if not key:
            logger.warning(
                "pix_key_not_found",
                extra={"user_id": user_id, "key_id": key_id},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pix Key not found",
            )
        
        # Check user ownership
        key_user_id = key.get("user_id") if isinstance(key, dict) else key.user_id
        if str(key_user_id) != str(user_id):
            logger.warning(
                "unauthorized_key_access",
                extra={"user_id": user_id, "key_id": key_id, "key_owner": key_user_id},
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this Pix Key",
            )
        
        logger.info(
            "pix_key_retrieved",
            extra={"user_id": user_id, "key_id": key_id},
        )
        
        return {
            "data": key,
            "message": "Pix Key retrieved successfully",
            "success": True,
        }
        
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(
            "get_key_unexpected_error",
            extra={
                "user_id": user_id,
                "key_id": key_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the key",
        ) from e
