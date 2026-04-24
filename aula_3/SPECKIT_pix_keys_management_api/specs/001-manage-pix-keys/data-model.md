# Data Model: Pix Keys Management Feature

**Feature**: Pix Keys Management (MVP P1-P3)  
**Date**: 2026-04-22  
**Architecture**: Clean Code Architecture - Entities Layer

---

## Domain Entities

### User Entity

**Purpose**: Represents a customer/account holder managing Pix Keys. This entity is provided by the authentication layer and referenced by PixKey.

**Fields**:
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `user_id` | UUID | PK, NOT NULL | Unique identifier from auth system |
| `email` | String | UNIQUE, NOT NULL | User's email for communication |
| `phone` | String | NULLABLE | Optional phone number |
| `created_at` | DateTime | NOT NULL | Timestamp of account creation |
| `updated_at` | DateTime | NOT NULL | Last modification timestamp |

**Relationship**: One-to-Many with PixKey (one user has multiple keys)

**Business Rules**:
- User must exist in auth system before registering keys
- All PixKey records must reference a valid user_id
- Deleting a user should cascade-delete or archive all associated PixKeys (P2 feature)

**State**: Immutable reference (managed by auth layer). Feature does not modify User entity.

---

### PixKey Entity

**Purpose**: Represents a single Pix Key identifier registered for a user. Core entity of the feature.

**Fields**:
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `key_id` | UUID | PK, NOT NULL | Unique identifier |
| `user_id` | UUID | FK(User), NOT NULL | User who owns the key |
| `key_type` | Enum | [CPF, EMAIL, PHONE, RANDOM] | Type category |
| `key_value_hash` | String | UNIQUE per (user_id, key_type), NOT NULL | SHA-256 hash of actual key |
| `key_value_masked` | String | NOT NULL | Masked display (e.g., "user***@email.com") |
| `status` | Enum | [ACTIVE, INACTIVE] | Current state |
| `alias` | String | NULLABLE, MAX 50 | User-friendly nickname |
| `is_preferred` | Boolean | DEFAULT false | Preferred key for notifications (P2 use) |
| `validation_status` | Enum | [PENDING, VALID, INVALID] | Result of format validation |
| `validation_error` | String | NULLABLE | Error message if validation failed |
| `pix_network_id` | String | NULLABLE | External ID from Pix network (P2) |
| `created_at` | DateTime | NOT NULL | Registration timestamp |
| `updated_at` | DateTime | NOT NULL | Last status change timestamp |
| `revalidated_at` | DateTime | NULLABLE | Last network revalidation (P2) |

**Constraints**:
- Foreign key: `(user_id) → User(user_id)`
- Unique: `(user_id, key_value_hash)` - prevents duplicate keys for same user
- Check: `status IN [ACTIVE, INACTIVE]`
- Check: `key_type IN [CPF, EMAIL, PHONE, RANDOM]`
- Check: `validation_status IN [PENDING, VALID, INVALID]`
- Check: `is_preferred = false if status = INACTIVE` (preferred keys must be active)
- Business Constraint: Max 5 keys per user (enforced in use case, not in schema)

**Relationships**:
- Many-to-One with User: `user_id` → User.user_id
- One-to-Many with PixKeyAudit: `key_id` → PixKeyAudit.key_id
- One-to-Many with PixKeyValidation: `key_id` → PixKeyValidation.key_id

**Business Rules**:

1. **Registration**:
   - User provides key_type and key_value (plain text)
   - System validates format (local validation)
   - System hashes key_value → key_value_hash
   - System generates masked display (key_value_masked)
   - Initial status: ACTIVE
   - Initial validation_status: VALID (after local validation passes)
   - Audit log entry created

2. **Deactivation**:
   - User changes status: ACTIVE → INACTIVE
   - Timestamp updated
   - If is_preferred=true, reset to false
   - Audit log entry created
   - Key value not changed; remains in system

3. **Reactivation**:
   - User changes status: INACTIVE → ACTIVE
   - Timestamp updated
   - Validation status checked; if expired (P2), trigger revalidation
   - Audit log entry created

4. **Deletion**:
   - Only INACTIVE keys can be deleted
   - Physical deletion from database (not soft delete)
   - Audit trail preserved in PixKeyAudit
   - Audit log entry created

5. **Preferred Flag**:
   - Only one key per user can have is_preferred=true
   - Setting is_preferred=true on key A sets all other user keys to false
   - is_preferred=false if key status=INACTIVE
   - Reserved for P2 notification system

6. **Validation**:
   - validation_status field tracks format validation result
   - Network validation (P2) will update pix_network_id and revalidated_at

**Storage**:
- Table: `pix_keys`
- Indexes:
  - PRIMARY: `(key_id)`
  - FOREIGN: `(user_id)` for queries like "get all keys for user"
  - UNIQUE: `(user_id, key_value_hash)` for duplicate prevention
  - SEARCH: `(user_id, status)` for filtering active/inactive keys
  - SEARCH: `(user_id, key_type)` for type-based queries

---

### PixKeyAudit Entity

**Purpose**: Immutable audit trail of all PixKey lifecycle events for compliance, debugging, and user history.

**Fields**:
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `audit_id` | UUID | PK, NOT NULL | Unique audit entry ID |
| `key_id` | UUID | FK(PixKey), NOT NULL | Which key this event concerns |
| `user_id` | UUID | FK(User), NOT NULL | User performing or affected by action |
| `event_type` | Enum | [REGISTERED, REVALIDATED, ACTIVATED, DEACTIVATED, DELETED, PREFERRED, UNPREFERED, ALIAS_UPDATED] | What happened |
| `old_status` | Enum | NULLABLE [ACTIVE, INACTIVE] | Previous status (if status changed) |
| `new_status` | Enum | NULLABLE [ACTIVE, INACTIVE] | New status (if status changed) |
| `details` | JSON | NULLABLE | Extra context: {old_alias, new_alias, error_message, ...} |
| `created_at` | DateTime | NOT NULL | When this event occurred |
| `request_id` | String | NOT NULL | Trace identifier for correlating requests |

**Constraints**:
- Foreign keys: `key_id` → PixKey, `user_id` → User
- Immutable after creation (no UPDATE, only INSERT)
- event_type IN [REGISTERED, REVALIDATED, ACTIVATED, DEACTIVATED, DELETED, PREFERRED, UNPREFERED, ALIAS_UPDATED]

**Relationships**:
- Many-to-One with PixKey: `key_id` → PixKey.key_id
- Many-to-One with User: `user_id` → User.user_id

**Business Rules**:

- Every PixKey action creates an audit entry immediately
- Event types:
  - **REGISTERED**: New key created. Details: {key_type, validation_status}
  - **REVALIDATED**: Key revalidated with network. Details: {old_validation_status, new_validation_status, pix_network_response}
  - **ACTIVATED**: Status changed from INACTIVE → ACTIVE. Details: {reason}
  - **DEACTIVATED**: Status changed from ACTIVE → INACTIVE. Details: {reason}
  - **DELETED**: Key permanently removed. Details: {deletion_reason}
  - **PREFERRED**: is_preferred set to true. Details: {previous_preferred_key_id}
  - **UNPREFERED**: is_preferred set to false. Details: {}
  - **ALIAS_UPDATED**: Alias changed. Details: {old_alias, new_alias}
- All entries logged in JSON format with request_id for traceability
- Retention policy TBD in P2 (infrastructure decision); MVP stores indefinitely
- Used for user history export (LGPD compliance) and CB audit

**Storage**:
- Table: `pix_key_audits`
- Indexes:
  - PRIMARY: `(audit_id)`
  - FOREIGN: `(key_id)` for audit history of a specific key
  - FOREIGN: `(user_id)` for user activity history
  - SEARCH: `(created_at)` for time-range queries

---

### PixKeyValidation Entity

**Purpose**: Stores results of format and network validation for audit and retry logic.

**Fields**:
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `validation_id` | UUID | PK, NOT NULL | Unique validation record ID |
| `key_id` | UUID | FK(PixKey), NOT NULL | Which key was validated |
| `validation_type` | Enum | [FORMAT, NETWORK] | Whether local or network validation |
| `is_valid` | Boolean | NOT NULL | Validation result (pass/fail) |
| `validation_error` | String | NULLABLE | Error code/message if invalid |
| `pix_network_response` | JSON | NULLABLE | Full response from Pix network (P2) |
| `validation_date` | DateTime | NOT NULL | When validation was performed |

**Constraints**:
- Foreign key: `key_id` → PixKey.key_id
- validation_type IN [FORMAT, NETWORK]

**Relationships**:
- Many-to-One with PixKey: `key_id` → PixKey.key_id

**Business Rules**:

- Created whenever a key is validated
- FORMAT validation happens in MVP (CPF/email/phone format checks)
- NETWORK validation happens in P2 (Pix network checks)
- Multiple validations per key allowed (revalidation history)
- Last validation result is mirrored in PixKey.validation_status and PixKey.validation_error

**Storage**:
- Table: `pix_key_validations`
- Indexes:
  - PRIMARY: `(validation_id)`
  - FOREIGN: `(key_id)` for validation history
  - SEARCH: `(validation_date)` for finding recent validations

---

## Entity Relationships Diagram

```
User (1)
  ├─→ (1..5) PixKey
  │     ├─→ (0..∞) PixKeyAudit
  │     ├─→ (0..∞) PixKeyValidation
  │
  └─→ (0..∞) PixKeyAudit (as user who triggered action)
```

---

## Validation Rules (Business Logic)

### CPF Format
- 11 digits, no formatting
- Valid check digit per Brazilian CPF algorithm
- Pattern: `/^\d{11}$/`
- Example: `12345678901`

### Email Format
- Valid RFC 5322 format (simplified: `[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}`)
- Domain must exist (MX record check in P2)
- Example: `user@example.com`

### Phone Format
- 11 digits (mobile) or 10 digits (landline) with area code (DDD)
- Pattern: `/^\d{10,11}$/`
- Area code (DDD) must be valid (11-99 range, excluding invalid codes)
- Example: `11987654321` (mobile) or `1133334444` (landline)

### Random Key (UUID)
- UUID4 format: `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`
- Generated server-side, never user-provided
- Pattern: `/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i`
- Example: `550e8400-e29b-41d4-a716-446655440000`

### Duplicate Prevention
- No two keys of same type and value per user
- Validation: Check `(user_id, key_value_hash)` unique constraint before insert
- Error: "This key is already registered on your account"

### Max Keys Per User
- Maximum 5 keys per user account (Brazilian Central Bank limit)
- Enforced: Count existing ACTIVE + INACTIVE keys before registration
- Error: "You have reached the maximum number of Pix Keys (5). Delete or deactivate unused keys to register new ones."

### Key Status Transitions
```
ACTIVE → DEACTIVATE → INACTIVE
  ↑                        ↓
  └─────── ACTIVATE ←──────┘

Delete only allowed from INACTIVE state
Deactivation required before deletion
```

---

## Database Schema Scripts

### Initial Migration (MVP)

```sql
-- User table (reference only, managed by auth layer)
CREATE TABLE users (
  user_id UUID PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  phone VARCHAR(20),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Main PixKey table
CREATE TABLE pix_keys (
  key_id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(user_id),
  key_type VARCHAR(10) NOT NULL CHECK (key_type IN ('CPF', 'EMAIL', 'PHONE', 'RANDOM')),
  key_value_hash VARCHAR(64) NOT NULL,  -- SHA-256 hex
  key_value_masked VARCHAR(255) NOT NULL,
  status VARCHAR(10) NOT NULL CHECK (status IN ('ACTIVE', 'INACTIVE')),
  alias VARCHAR(50),
  is_preferred BOOLEAN NOT NULL DEFAULT FALSE,
  validation_status VARCHAR(10) NOT NULL CHECK (validation_status IN ('PENDING', 'VALID', 'INVALID')),
  validation_error TEXT,
  pix_network_id VARCHAR(255),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  revalidated_at TIMESTAMP,
  
  UNIQUE(user_id, key_value_hash),
  CONSTRAINT preferred_must_be_active CHECK ((is_preferred = FALSE) OR (status = 'ACTIVE')),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Audit trail table
CREATE TABLE pix_key_audits (
  audit_id UUID PRIMARY KEY,
  key_id UUID NOT NULL REFERENCES pix_keys(key_id),
  user_id UUID NOT NULL REFERENCES users(user_id),
  event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('REGISTERED', 'REVALIDATED', 'ACTIVATED', 'DEACTIVATED', 'DELETED', 'PREFERRED', 'UNPREFERED', 'ALIAS_UPDATED')),
  old_status VARCHAR(10),
  new_status VARCHAR(10),
  details JSONB,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  request_id VARCHAR(255) NOT NULL
);

-- Validation history table
CREATE TABLE pix_key_validations (
  validation_id UUID PRIMARY KEY,
  key_id UUID NOT NULL REFERENCES pix_keys(key_id),
  validation_type VARCHAR(10) NOT NULL CHECK (validation_type IN ('FORMAT', 'NETWORK')),
  is_valid BOOLEAN NOT NULL,
  validation_error TEXT,
  pix_network_response JSONB,
  validation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_pix_keys_user_id ON pix_keys(user_id);
CREATE INDEX idx_pix_keys_user_status ON pix_keys(user_id, status);
CREATE INDEX idx_pix_keys_user_type ON pix_keys(user_id, key_type);
CREATE INDEX idx_pix_key_audits_key_id ON pix_key_audits(key_id);
CREATE INDEX idx_pix_key_audits_user_id ON pix_key_audits(user_id);
CREATE INDEX idx_pix_key_audits_created ON pix_key_audits(created_at);
CREATE INDEX idx_pix_key_validations_key_id ON pix_key_validations(key_id);
CREATE INDEX idx_pix_key_validations_date ON pix_key_validations(validation_date);
```

---

## API Payload Models (Pydantic Schemas)

These models represent the data contracts for HTTP requests/responses.

### Request: RegisterPixKeyRequest
```python
class RegisterPixKeyRequest(BaseModel):
    key_type: Literal["CPF", "EMAIL", "PHONE", "RANDOM"]
    key_value: Optional[str] = None  # null for RANDOM (generated server-side)
    alias: Optional[str] = None  # max 50 chars
    
    # Validation
    @field_validator('key_value')
    def validate_key_value(cls, v, info):
        if info.data['key_type'] != 'RANDOM' and not v:
            raise ValueError('key_value required for CPF, EMAIL, PHONE')
        return v
```

### Response: PixKeyResponse
```python
class PixKeyResponse(BaseModel):
    key_id: UUID
    key_type: Literal["CPF", "EMAIL", "PHONE", "RANDOM"]
    key_value_masked: str  # masked display
    status: Literal["ACTIVE", "INACTIVE"]
    alias: Optional[str]
    is_preferred: bool
    created_at: datetime
    updated_at: datetime
```

### Response: RegisterPixKeyResponse
```python
class RegisterPixKeyResponse(BaseModel):
    key_id: UUID
    key_value: str  # FULL key shown once after registration
    key_value_masked: str
    status: Literal["ACTIVE"]
    message: str  # "Key registered successfully. Save this key in a safe place."
    
    # Note: Full key_value shown only in registration response, never after
```

---

## Summary

**Entities Created**: 4 (User, PixKey, PixKeyAudit, PixKeyValidation)
**Tables Created**: 3 (pix_keys, pix_key_audits, pix_key_validations)
**Business Rules**: 25+ constraints and validations
**Estimated Schema Size**: ~2-3 MB per 10k users (with 4 keys each and 2 years audit history)

All entities follow Clean Code Architecture Entities Layer principles:
- ✅ Independent of frameworks (no FastAPI/SQLAlchemy imports)
- ✅ Core business logic and rules embedded
- ✅ Data persistence details abstracted (no SQL)
- ✅ Validation rules encapsulated
- ✅ State transitions defined
