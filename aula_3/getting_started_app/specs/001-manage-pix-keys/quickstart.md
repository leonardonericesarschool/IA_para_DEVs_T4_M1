# Quick Start: Pix Keys Management Feature

**Feature**: Pix Keys Management - MVP (P1-P3)  
**Date**: 2026-04-22  
**Status**: Design Complete, Ready for Implementation  
**Architecture**: Python Clean Code Architecture with FastAPI

---

## Feature Overview

Users can register, view, and manage their Pix Keys (CPF, email, phone, or random identifiers) to receive instant payments through the Brazilian Pix payment system. This MVP delivers the core functionality for managing payment identifiers with a focus on reliability and user control.

**Key Capabilities**:
1. Register new Pix Keys (4 types: CPF, Email, Phone, Random)
2. View all registered keys with masked sensitive data
3. Deactivate/Reactivate keys to control payment receiving
4. Delete deactivated keys to keep list clean
5. Edit key metadata (alias, preferred flag)
6. Search/filter keys by type and status
7. Complete audit trail for compliance

**Target Users**: Any customer who wants to receive payments via Pix

---

## MVP Scope & Priorities

### Priority P1 (Core MVP - 4 User Stories)
- ✅ **Story 1**: Register a Pix Key
- ✅ **Story 2**: View registered Pix Keys
- ✅ **Story 3**: Deactivate/Reactivate a Pix Key

### Priority P2 (Follow-up Release)
- 📋 **Story 4**: Delete a Pix Key (deactivation required first)
- 📋 **Story 5**: Edit Pix Key details (alias, preferred flag)

### Priority P3 (Polish & Scale)
- 📋 **Story 6**: Search and filter Pix Keys by type/status

---

## Technical Architecture

### Layer Breakdown

```
┌─────────────────────────────────────────────────────────┐
│ Frameworks & Drivers (FastAPI, SQLAlchemy)              │
├─────────────────────────────────────────────────────────┤
│ Interface Adapters (Controllers, Repositories)          │
│  • PixKeyController (HTTP handlers)                     │
│  • PixKeyRepository (Data access)                       │
├─────────────────────────────────────────────────────────┤
│ Application Rules (Use Cases/Interactors)              │
│  • RegisterPixKeyUseCase                                │
│  • DeactivatePixKeyUseCase                              │
│  • ViewPixKeysUseCase                                   │
├─────────────────────────────────────────────────────────┤
│ Enterprise Rules (Entities)                             │
│  • PixKey                                               │
│  • PixKeyValidator                                      │
│  • PixKeyAudit                                          │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Language**: Python 3.9+
- **Web Framework**: FastAPI (async)
- **ORM**: SQLAlchemy 2.0+ (async driver)
- **Database**: PostgreSQL
- **Testing**: pytest with pytest-cov (80% coverage target)
- **Validation**: Pydantic v2
- **Dependency Injection**: Manual or Dependency Injector library
- **Logging**: python-json-logger (structured JSON logs)
- **Code Quality**: Black, Ruff, mypy

### Project Structure

```
src/
├── pix_keys/
│   ├── entities/
│   │   ├── pix_key.py           # Domain model
│   │   ├── pix_key_validator.py # Business rules
│   │   └── pix_key_audit.py     # Audit trail model
│   │
│   ├── use_cases/
│   │   ├── register_pix_key.py
│   │   ├── view_pix_keys.py
│   │   ├── deactivate_pix_key.py
│   │   └── edit_pix_key.py
│   │
│   ├── controllers/
│   │   └── pix_key_controller.py  # FastAPI routes
│   │
│   ├── gateways/
│   │   ├── pix_network_gateway.py # Pix integration (stub)
│   │   └── audit_log_gateway.py
│   │
│   ├── repositories/
│   │   ├── pix_key_repository.py  # ABC interface
│   │   └── sqlalchemy_pix_key_repository.py
│   │
│   └── config.py                  # DI container & configuration

tests/
├── unit/
│   ├── test_pix_key_validator.py
│   ├── test_register_pix_key_case.py
│   └── ...
│
├── integration/
│   ├── test_pix_key_repository.py
│   ├── test_pix_key_controller.py
│   └── ...
│
└── contract/
    └── test_api_contracts.py

requirements.txt
```

---

## Data Model Summary

**Main Entities**:
1. **PixKey**: Registered Pix Key with status, type, and validation
2. **PixKeyAudit**: Immutable audit trail of all key events
3. **PixKeyValidation**: Format and network validation results
4. **User**: Reference to authenticated user (auth layer)

**Key Constraints**:
- Max 5 keys per user (Brazilian Central Bank limit)
- No duplicate keys per user (unique constraint)
- Preferred flag only on active keys
- Deletion only allowed for inactive keys
- Sensitive data masked in UI and logs

See [data-model.md](data-model.md) for complete schema definition.

---

## API Contracts

**Base URL**: `/api/v1/pix-keys`  
**Authentication**: Bearer token (JWT)

**Core Endpoints**:

| Method | Endpoint | User Story | Priority |
|--------|----------|------------|----------|
| POST | /register | Register Key | P1 |
| GET | /list | View Keys | P1 |
| PUT | /{id}/deactivate | Deactivate | P1 |
| PUT | /{id}/activate | Reactivate | P1 |
| PUT | /{id}/edit | Edit Metadata | P2 |
| DELETE | /{id} | Delete Key | P2 |
| GET | /search | Search/Filter | P3 |
| GET | /{id}/audit-trail | Audit Trail | Admin |

**Response Format**:
```json
{
  "success": true,
  "data": { /* payload */ },
  "request_id": "uuid"
}
```

See [contracts/api-contracts.md](contracts/api-contracts.md) for detailed endpoint specifications.

---

## Key Features & Decisions

### 1. Key Type Support
- **CPF** (11 digits with check digit validation)
- **Email** (RFC 5322 format, domain validation in P2)
- **Phone** (11 digits mobile or 10 digits landline, DDD validation)
- **Random** (UUID4, generated server-side)

### 2. Validation Strategy
- **Format Validation** (MVP): Local validation against Brazilian standards
- **Network Validation** (P2): Integration with Pix DICT API (stub ready)
- **Duplicate Prevention**: Application-level check + database unique constraint

### 3. Key Status Model
```
ACTIVE ←→ INACTIVE ← DELETE (INACTIVE only)
```
- Two-state model (no pending, no expired in MVP)
- Deactivation required before deletion (safety measure)
- Reactivation from inactive is allowed

### 4. Data Security
- **Plaintext Keys**: Shown only once after registration
- **Storage**: SHA-256 hash in database, never plaintext
- **Display**: Masked format (e.g., "user***@email.com")
- **Logs**: Hashed format, never full key
- **API Responses**: Always masked (except registration confirmation)

### 5. Audit Trail
- **Events**: REGISTERED, ACTIVATED, DEACTIVATED, DELETED, PREFERRED, ALIAS_UPDATED
- **Immutable**: Audit records never updated, only inserted
- **Traceability**: Request ID links events to API calls
- **Compliance**: Supports LGPD data export and Central Bank audits

### 6. Preferred Key Flag
- **MVP**: Data model ready; no functional use yet
- **P2+**: Used for notification delivery and default payment method
- **Constraint**: Only one key per user can be preferred
- **Enforcement**: is_preferred=false if status=INACTIVE

---

## Use Case Workflows

### Use Case 1: Register Pix Key

**Actors**: User, System

**Flow**:
1. User submits registration form (key_type, key_value, optional alias)
2. System validates format (CPF/email/phone/random)
3. System checks for duplicates (user cannot have same key twice)
4. System checks limit (user cannot exceed 5 keys)
5. System hashes key and creates masked display
6. System creates PixKey record with ACTIVE status
7. System creates audit entry (REGISTERED)
8. System returns registration confirmation with FULL key (shown once)

**Exception Handling**:
- Invalid format → VALIDATION_ERROR with field-level messages
- Duplicate key → KEY_ALREADY_EXISTS with existing key info
- Limit exceeded → MAX_KEYS_EXCEEDED with guidance to delete/deactivate
- Database error → INTERNAL_ERROR with request_id for debugging

### Use Case 2: View Pix Keys

**Actors**: User, System

**Flow**:
1. User requests key list (optional filtering/sorting)
2. System retrieves all keys for authenticated user
3. System applies filters (status, type)
4. System sorts by requested field
5. System returns paginated list with masked values

**Output**: List with masked key values, status, alias, metadata

### Use Case 3: Deactivate Pix Key

**Actors**: User, System

**Flow**:
1. User selects key and confirms deactivation
2. System validates key exists and is ACTIVE
3. System updates status: ACTIVE → INACTIVE
4. System resets is_preferred to false (if was preferred)
5. System creates audit entry (DEACTIVATED)
6. System returns updated key

**Exception Handling**:
- Key not found → KEY_NOT_FOUND
- Already inactive → INVALID_STATUS_TRANSITION

### Use Case 4: Reactivate Pix Key

**Actors**: User, System

**Flow**:
1. User selects inactive key and confirms activation
2. System validates key exists and is INACTIVE
3. System updates status: INACTIVE → ACTIVE
4. System creates audit entry (ACTIVATED)
5. System returns updated key

### Use Case 5: Delete Pix Key (P2)

**Actors**: User, System

**Flow**:
1. User selects inactive key and confirms deletion
2. System validates key exists and is INACTIVE
3. System validates user hasn't marked as preferred
4. System physically deletes from database
5. System creates audit entry (DELETED)
6. System returns confirmation

**Exception Handling**:
- Key active → CANNOT_DELETE_ACTIVE_KEY
- Not found → KEY_NOT_FOUND

### Use Case 6: Edit Pix Key (P2)

**Actors**: User, System

**Flow**:
1. User submits edit (alias and/or is_preferred)
2. System validates changes (preferred keys must be active)
3. If is_preferred=true: reset all other keys to false
4. System updates PixKey record
5. System creates audit entries (ALIAS_UPDATED, PREFERRED/UNPREFERED)
6. System returns updated key

---

## Test Strategy

### Coverage Targets
- **Unit Tests**: 80%+ code coverage (entities, use cases)
- **Integration Tests**: Repository contracts, database operations
- **Contract Tests**: API endpoint behavior, error responses

### Test Breakdown

**Unit Tests** (test/unit/):
```python
# Entities
- test_pix_key_creation()
- test_pix_key_validation_cpf()
- test_pix_key_validation_email()
- test_pix_key_validation_phone()
- test_pix_key_status_transitions()
- test_pix_key_max_per_user()
- test_pix_key_duplicate_prevention()

# Use Cases
- test_register_valid_key()
- test_register_duplicate_key()
- test_register_exceeds_limit()
- test_deactivate_active_key()
- test_deactivate_already_inactive()
- test_view_keys_filters()
```

**Integration Tests** (test/integration/):
```python
# Repository
- test_create_pix_key()
- test_find_by_user()
- test_update_status()
- test_delete_pix_key()

# Controller (with mock use cases)
- test_register_endpoint_201()
- test_list_endpoint_returns_keys()
- test_deactivate_endpoint_updates_status()
- test_invalid_request_returns_400()
```

**Contract Tests** (test/contract/):
```python
# API Contracts
- test_register_response_schema()
- test_error_response_schema()
- test_list_pagination()
- test_status_code_mapping()
```

---

## Deployment & Rollout

### Phase 0 (Complete): Research & Clarifications ✅
- Pix integration patterns researched
- Brazilian standards documented
- All technical unknowns resolved

### Phase 1 (Next): Design & Architecture ✅
- Data model designed
- API contracts defined
- Use case workflows documented
- Repository pattern ready for implementation

### Phase 2 (Following): Implementation
- Development tasks generated from design
- Code written layer-by-layer (Entities → Use Cases → Controllers)
- Tests written first (TDD)
- Code review and merge

### Phase 3: Integration Testing
- End-to-end workflows tested
- Error scenarios validated
- Performance testing (if needed)
- User acceptance testing

### Phase 4: Deployment
- Database migrations run
- Feature flag enabled
- Monitoring and logging configured
- Release to production

---

## References

- **Specification**: [spec.md](spec.md)
- **Research**: [research.md](research.md)
- **Data Model**: [data-model.md](data-model.md)
- **API Contracts**: [contracts/api-contracts.md](contracts/api-contracts.md)
- **Constitution**: [.specify/memory/constitution.md](.specify/memory/constitution.md)

---

## Next Steps

1. **Setup Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Create Entity Classes** (Entities layer)
   - Implement PixKey, PixKeyValidator, PixKeyAudit

3. **Implement Use Cases** (Application layer)
   - RegisterPixKeyUseCase, ViewPixKeysUseCase, etc.

4. **Write Unit Tests** (80%+ coverage target)
   - Test-driven development: tests first

5. **Implement Repository & SQL** (Interface Adapters layer)
   - SQLAlchemy implementation of PixKeyRepository

6. **Build FastAPI Controllers** (Frameworks layer)
   - HTTP endpoints matching contracts

7. **Integration Testing**
   - End-to-end workflows with real database

8. **Code Review & Merge**
   - Review against Constitution requirements

---

**Ready for implementation. All design gates passed. Constitution alignment verified.**
