# API Contracts: Pix Keys Management Feature

**Feature**: Pix Keys Management  
**Format**: REST API contracts (FastAPI)  
**Date**: 2026-04-22  
**Architecture Layer**: Interface Adapters (Controllers)

---

## Overview

This document defines the HTTP API contracts for the Pix Keys Management feature. Each contract corresponds to one or more user stories. All endpoints require authentication (user_id provided via JWT token or middleware).

**Base Path**: `/api/v1/pix-keys`  
**Authentication**: Bearer token in Authorization header  
**Error Format**: Standard error response (see Error Handling section)

---

## User Story 1: Register a Pix Key (Priority P1)

### Endpoint: POST /api/v1/pix-keys/register

**Purpose**: Register a new Pix Key for the authenticated user. Supports CPF, email, phone, or random key types.

**Request**:
```json
POST /api/v1/pix-keys/register
Authorization: Bearer {token}
Content-Type: application/json

{
  "key_type": "email",          // CPF | EMAIL | PHONE | RANDOM
  "key_value": "user@example.com",  // string; null for RANDOM
  "alias": "Work Email"         // optional, max 50 chars
}
```

**Request Schema** (Pydantic):
```python
class RegisterPixKeyRequest(BaseModel):
    key_type: Literal["CPF", "EMAIL", "PHONE", "RANDOM"]
    key_value: Optional[str] = None
    alias: Optional[str] = Field(None, max_length=50)
    
    @field_validator('key_type')
    def validate_key_type(cls, v):
        if v not in ["CPF", "EMAIL", "PHONE", "RANDOM"]:
            raise ValueError('Invalid key_type')
        return v
    
    @field_validator('key_value')
    def validate_key_value(cls, v, info):
        key_type = info.data.get('key_type')
        if key_type != 'RANDOM' and not v:
            raise ValueError('key_value required for CPF, EMAIL, PHONE')
        if key_type == 'RANDOM' and v:
            raise ValueError('key_value must be null for RANDOM')
        return v
```

**Success Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "key_id": "550e8400-e29b-41d4-a716-446655440000",
    "key_type": "email",
    "key_value": "user@example.com",      // SHOWN ONLY in registration response
    "key_value_masked": "user***@example.com",
    "status": "ACTIVE",
    "alias": "Work Email",
    "is_preferred": false,
    "validation_status": "VALID",
    "created_at": "2026-04-22T10:30:00Z",
    "updated_at": "2026-04-22T10:30:00Z",
    "message": "Pix Key registered successfully. Save this key in a safe place for future reference."
  }
}
```

**Error Responses**:

**400 Bad Request** - Validation failed:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid CPF format",
    "details": {
      "fields": {
        "key_value": "CPF must have 11 digits"
      }
    }
  }
}
```

**409 Conflict** - Key already registered:
```json
{
  "success": false,
  "error": {
    "code": "KEY_ALREADY_EXISTS",
    "message": "This key is already registered on your account",
    "details": {
      "key_id": "existing-key-uuid",
      "status": "ACTIVE"
    }
  }
}
```

**429 Too Many Keys** - Exceeded maximum:
```json
{
  "success": false,
  "error": {
    "code": "MAX_KEYS_EXCEEDED",
    "message": "You have reached the maximum number of Pix Keys (5). Delete or deactivate unused keys to register new ones.",
    "details": {
      "max_allowed": 5,
      "current_count": 5
    }
  }
}
```

---

## User Story 2: View Registered Pix Keys (Priority P1)

### Endpoint: GET /api/v1/pix-keys/list

**Purpose**: Retrieve all Pix Keys for the authenticated user with status and metadata.

**Request**:
```
GET /api/v1/pix-keys/list
Authorization: Bearer {token}
```

**Query Parameters** (Optional):
- `status`: ACTIVE | INACTIVE (filter by status)
- `key_type`: CPF | EMAIL | PHONE | RANDOM (filter by type)
- `sort_by`: created_at | updated_at | key_type (default: created_at desc)
- `page`: integer (pagination, default: 1)
- `limit`: integer (page size, default: 20)

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "keys": [
      {
        "key_id": "550e8400-e29b-41d4-a716-446655440000",
        "key_type": "email",
        "key_value_masked": "user***@example.com",
        "status": "ACTIVE",
        "alias": "Work Email",
        "is_preferred": true,
        "created_at": "2026-04-22T10:30:00Z",
        "updated_at": "2026-04-22T10:30:00Z"
      },
      {
        "key_id": "660e8400-e29b-41d4-a716-446655440001",
        "key_type": "cpf",
        "key_value_masked": "***.***.***-42",
        "status": "INACTIVE",
        "alias": "Personal CPF",
        "is_preferred": false,
        "created_at": "2026-04-21T15:00:00Z",
        "updated_at": "2026-04-22T09:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 2,
      "total_pages": 1
    }
  }
}
```

**Empty List Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "keys": [],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 0,
      "total_pages": 0
    },
    "message": "No Pix Keys registered yet. Register your first key to receive payments."
  }
}
```

---

## User Story 3: Deactivate a Pix Key (Priority P1)

### Endpoint: PUT /api/v1/pix-keys/{key_id}/deactivate

**Purpose**: Change a Pix Key status from ACTIVE to INACTIVE, preventing it from receiving payments.

**Request**:
```
PUT /api/v1/pix-keys/550e8400-e29b-41d4-a716-446655440000/deactivate
Authorization: Bearer {token}
```

**Request Body** (Optional confirmation):
```json
{
  "confirm": true,
  "reason": "No longer using this email"  // optional audit reason
}
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "key_id": "550e8400-e29b-41d4-a716-446655440000",
    "key_type": "email",
    "key_value_masked": "user***@example.com",
    "status": "INACTIVE",
    "alias": "Work Email",
    "is_preferred": false,  // reset to false if was preferred
    "created_at": "2026-04-22T10:30:00Z",
    "updated_at": "2026-04-22T10:35:00Z"
  },
  "message": "Pix Key deactivated successfully. It will no longer receive payments."
}
```

**Error Responses**:

**404 Not Found** - Key does not exist:
```json
{
  "success": false,
  "error": {
    "code": "KEY_NOT_FOUND",
    "message": "Pix Key not found",
    "details": {
      "key_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  }
}
```

**400 Bad Request** - Already inactive:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_STATUS_TRANSITION",
    "message": "This key is already inactive and cannot be deactivated again",
    "details": {
      "current_status": "INACTIVE",
      "action": "deactivate"
    }
  }
}
```

---

## User Story 3b: Reactivate a Pix Key (Priority P1)

### Endpoint: PUT /api/v1/pix-keys/{key_id}/activate

**Purpose**: Change a Pix Key status from INACTIVE back to ACTIVE.

**Request**:
```
PUT /api/v1/pix-keys/550e8400-e29b-41d4-a716-446655440000/activate
Authorization: Bearer {token}
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "key_id": "550e8400-e29b-41d4-a716-446655440000",
    "key_type": "email",
    "key_value_masked": "user***@example.com",
    "status": "ACTIVE",
    "alias": "Work Email",
    "is_preferred": false,
    "created_at": "2026-04-22T10:30:00Z",
    "updated_at": "2026-04-22T10:40:00Z"
  },
  "message": "Pix Key reactivated successfully. It can now receive payments."
}
```

---

## User Story 4: Delete a Pix Key (Priority P2)

### Endpoint: DELETE /api/v1/pix-keys/{key_id}

**Purpose**: Permanently remove an inactive Pix Key from the account.

**Request**:
```
DELETE /api/v1/pix-keys/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer {token}
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "key_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Pix Key deleted permanently and cannot be recovered."
  }
}
```

**Error Response** - Key is active:
```json
{
  "success": false,
  "error": {
    "code": "CANNOT_DELETE_ACTIVE_KEY",
    "message": "Active keys cannot be deleted. Deactivate this key first before deleting.",
    "details": {
      "key_id": "550e8400-e29b-41d4-a716-446655440000",
      "current_status": "ACTIVE",
      "required_action": "Deactivate first"
    }
  }
}
```

---

## User Story 5: Edit Pix Key Details (Priority P2)

### Endpoint: PUT /api/v1/pix-keys/{key_id}/edit

**Purpose**: Update metadata for a registered Pix Key (alias, preferred flag).

**Request**:
```json
PUT /api/v1/pix-keys/550e8400-e29b-41d4-a716-446655440000/edit
Authorization: Bearer {token}
Content-Type: application/json

{
  "alias": "Updated Work Email",
  "is_preferred": true
}
```

**Request Schema** (Pydantic):
```python
class EditPixKeyRequest(BaseModel):
    alias: Optional[str] = Field(None, max_length=50)
    is_preferred: Optional[bool] = None
    
    # At least one field must be present
    @model_validator(mode='after')
    def validate_has_update(self):
        if self.alias is None and self.is_preferred is None:
            raise ValueError('At least one field (alias or is_preferred) must be provided')
        return self
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "key_id": "550e8400-e29b-41d4-a716-446655440000",
    "key_type": "email",
    "key_value_masked": "user***@example.com",
    "status": "ACTIVE",
    "alias": "Updated Work Email",
    "is_preferred": true,
    "created_at": "2026-04-22T10:30:00Z",
    "updated_at": "2026-04-22T11:00:00Z"
  },
  "message": "Pix Key updated successfully."
}
```

**Error Response** - Setting preferred on inactive key:
```json
{
  "success": false,
  "error": {
    "code": "CANNOT_PREFER_INACTIVE_KEY",
    "message": "Only active keys can be marked as preferred. Activate this key first.",
    "details": {
      "key_id": "550e8400-e29b-41d4-a716-446655440000",
      "current_status": "INACTIVE"
    }
  }
}
```

---

## User Story 6: Search and Filter Pix Keys (Priority P3)

### Endpoint: GET /api/v1/pix-keys/search

**Purpose**: Search and filter Pix Keys by type, status, or alias.

**Request**:
```
GET /api/v1/pix-keys/search?key_type=email&status=ACTIVE&q=work&sort_by=created_at
Authorization: Bearer {token}
```

**Query Parameters**:
- `q`: Search term (searches in alias field, case-insensitive)
- `key_type`: CPF | EMAIL | PHONE | RANDOM (exact match)
- `status`: ACTIVE | INACTIVE (exact match)
- `sort_by`: created_at | updated_at | key_type | alias (default: created_at desc)
- `page`: integer (pagination)
- `limit`: integer (page size, default: 20)

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "keys": [
      {
        "key_id": "550e8400-e29b-41d4-a716-446655440000",
        "key_type": "email",
        "key_value_masked": "user***@example.com",
        "status": "ACTIVE",
        "alias": "Work Email",
        "is_preferred": true,
        "created_at": "2026-04-22T10:30:00Z",
        "updated_at": "2026-04-22T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 1,
      "total_pages": 1
    }
  }
}
```

---

## Admin Endpoint: Get Audit Trail

### Endpoint: GET /api/v1/pix-keys/{key_id}/audit-trail

**Purpose**: Retrieve complete audit history for a Pix Key (for support/compliance).

**Request**:
```
GET /api/v1/pix-keys/550e8400-e29b-41d4-a716-446655440000/audit-trail
Authorization: Bearer {admin_token}
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "key_id": "550e8400-e29b-41d4-a716-446655440000",
    "events": [
      {
        "audit_id": "audit-001",
        "event_type": "REGISTERED",
        "old_status": null,
        "new_status": "ACTIVE",
        "details": {
          "key_type": "email",
          "validation_status": "VALID"
        },
        "created_at": "2026-04-22T10:30:00Z",
        "request_id": "req-001"
      },
      {
        "audit_id": "audit-002",
        "event_type": "PREFERRED",
        "old_status": null,
        "new_status": null,
        "details": {
          "previous_preferred_key_id": null
        },
        "created_at": "2026-04-22T10:35:00Z",
        "request_id": "req-002"
      }
    ]
  }
}
```

---

## Error Handling

All error responses follow this standard format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",         // Machine-readable error identifier
    "message": "Human message",    // User-friendly error message
    "details": {}                  // Optional context specific to error
  },
  "request_id": "uuid"             // Request ID for tracing
}
```

**Standard Error Codes**:
- `VALIDATION_ERROR`: Invalid request data
- `AUTHENTICATION_ERROR`: Missing or invalid auth token
- `AUTHORIZATION_ERROR`: User not allowed to access resource
- `KEY_NOT_FOUND`: Pix Key does not exist
- `KEY_ALREADY_EXISTS`: Duplicate key registration attempt
- `MAX_KEYS_EXCEEDED`: User exceeded max 5 keys limit
- `INVALID_STATUS_TRANSITION`: Invalid state change (e.g., deactivate inactive key)
- `CANNOT_DELETE_ACTIVE_KEY`: Attempted to delete active key
- `CANNOT_PREFER_INACTIVE_KEY`: Attempted to mark inactive key as preferred
- `INTERNAL_ERROR`: Unexpected server error

**HTTP Status Codes**:
- `200 OK`: Successful read/update
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing/invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Business rule violation (duplicate, status mismatch, etc.)
- `429 Too Many Requests`: Rate limited or max resources exceeded
- `500 Internal Server Error`: Unexpected error

---

## Response Metadata

Every response includes:
```json
{
  "success": true|false,
  "data": {},          // Response payload
  "error": {},         // Error object (if success=false)
  "request_id": "uuid" // For tracing and debugging
}
```

---

## Summary

**Endpoints**: 8 main + 1 admin
- ✅ POST /pix-keys/register (P1)
- ✅ GET /pix-keys/list (P1)
- ✅ PUT /pix-keys/{id}/deactivate (P1)
- ✅ PUT /pix-keys/{id}/activate (P1)
- ✅ PUT /pix-keys/{id}/edit (P2)
- ✅ DELETE /pix-keys/{id} (P2)
- ✅ GET /pix-keys/search (P3)
- ✅ GET /pix-keys/{id}/audit-trail (Admin/Compliance)

**Response Format**: RESTful JSON with standardized error handling
**Authentication**: Bearer token (JWT) via middleware
**Validation**: Pydantic schemas with comprehensive validation
**Audit**: Request ID tracking for all operations
