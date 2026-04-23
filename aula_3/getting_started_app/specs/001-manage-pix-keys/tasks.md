---
description: "Task list for Pix Keys Management feature implementation"
---

# Tasks: Pix Keys Management App

**Input**: Design documents from `/specs/001-manage-pix-keys/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, api-contracts.md
**Architecture**: Clean Code Architecture (Entities → Use Cases → Controllers → Frameworks)
**Testing Strategy**: Test-First Development (TDD - write tests first, then implement)

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this belongs to (US1, US2, US3, US4, US5)
- **Includes**: Exact file paths; assumes single project structure (src/, tests/ at repo root)

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create project structure and configure development environment

- [x] T001 Create FastAPI project structure with src/ and tests/ directories
- [x] T002 [P] Initialize requirements.txt with FastAPI, SQLAlchemy, Pydantic, pytest, python-json-logger dependencies
- [x] T003 [P] Configure pytest.ini with coverage targets (80%+) in tests/
- [x] T004 [P] Create pyproject.toml with project metadata and tool configurations (Black, Ruff, mypy)
- [x] T005 Create .gitignore with Python, pytest, and IDE patterns
- [x] T006 Initialize git hooks configuration (.pre-commit-config.yaml) for linting and type checking

---

## Phase 2: Foundational Infrastructure (Blocking Prerequisites)

**Purpose**: Core infrastructure MUST be complete before ANY user story work can begin

⚠️ **CRITICAL**: No user story implementation can begin until this phase is complete

### Database & ORM Setup

- [x] T007 Configure PostgreSQL connection management in src/config.py with dependency injection support
- [x] T008 [P] Create SQLAlchemy Base and database session factory in src/database.py
- [x] T009 [P] Create database migration framework structure (Alembic) in migrations/

### Domain Layer (Entities)

- [x] T010 [P] Create User entity reference in src/entities/user.py (mock for auth layer integration)
- [x] T011 [P] Create PixKeyType enum in src/entities/enums.py (CPF, EMAIL, PHONE, RANDOM)
- [x] T012 [P] Create PixKeyStatus enum in src/entities/enums.py (ACTIVE, INACTIVE)
- [x] T013 [P] Create PixKeyValidationStatus enum in src/entities/enums.py (PENDING, VALID, INVALID)

### Logging & Observability

- [x] T014 Create structured JSON logger setup in src/logging_config.py with request_id tracking
- [x] T015 [P] Create logging middleware for FastAPI in src/middleware/logging_middleware.py

### Error Handling & Validation

- [x] T016 [P] Create custom exception hierarchy in src/exceptions.py (DomainException, ApplicationException, PixKeyError, ValidationError)
- [x] T017 [P] Create exception handler middleware in src/middleware/exception_handler.py for HTTP response mapping
- [x] T018 Create validation utilities in src/utils/validators.py (CPF, email, phone validation functions)

### Repository Pattern (Abstraction Layer)

- [x] T019 Create abstract PixKeyRepository interface in src/repositories/pix_key_repository.py (ABC with CRUD methods)
- [x] T020 [P] Create PixKeyAuditRepository interface in src/repositories/pix_key_audit_repository.py (ABC for audit logs)

### Dependency Injection Container

- [x] T021 Create DI container setup in src/container.py with dependency registration (FastAPI Depends pattern or Dependency Injector library)

**Checkpoint**: Foundation complete. All user stories can now be implemented independently.

---

## Phase 3: User Story 1 - Register Pix Key (Priority: P1) 🎯 MVP

**Goal**: Users can register a new Pix Key (CPF, email, phone, or random) and receive confirmation

**Independent Test**: Fully testable by registering one key type and verifying it appears in the list with "active" status

### Tests for User Story 1 (TDD - Write First) 📝

> **IMPORTANT: Write these tests FIRST, ensure they FAIL, then implement to make them PASS**

- [x] T022 [P] [US1] Unit test: PixKey entity validation rules in tests/unit/entities/test_pix_key_entity.py
  - Test CPF format validation (11 digits)
  - Test email format validation
  - Test phone format validation
  - Test random key generation
  - Test masking logic (email mask, CPF mask, phone mask)

- [ ] T023 [P] [US1] Unit test: RegisterPixKeyUseCase in tests/unit/use_cases/test_register_pix_key_use_case.py
  - Test successful registration with valid CPF
  - Test successful registration with valid email
  - Test successful registration with valid phone
  - Test successful generation of random key
  - Test duplicate key prevention (same user, same key_type + key_value)
  - Test max keys limit (fail at 6th key when limit is 5)
  - Test validation error on invalid CPF
  - Test validation error on invalid email
  - Test validation error on invalid phone format

- [ ] T024 [P] [US1] Contract test: POST /api/v1/pix-keys/register endpoint in tests/contract/test_register_pix_key_endpoint.py
  - Test 201 response on successful registration with result data
  - Test 400 response on invalid format
  - Test 409 response on duplicate key
  - Test 429 response on max keys exceeded
  - Test 401 response on missing auth token
  - Test response structure (success, data, message fields)

- [ ] T025 [P] [US1] Integration test: Full registration flow in tests/integration/test_register_pix_key_flow.py
  - Test database persistence (key in DB after registration)
  - Test audit log creation (entry in pix_key_audits table)
  - Test JSON logging output format
  - Test response masking (plaintext only in response, masked in DB)

### Entity Implementation for User Story 1

- [x] T026 [P] [US1] Implement PixKey entity in src/entities/pix_key.py with:
  - Properties: key_id, user_id, key_type, key_value_hash, key_value_masked, status, alias, is_preferred, validation_status, created_at, updated_at
  - Methods: validate_format(), hash_key_value(), mask_key_value(), get_display_value()
  - Business rules: max 5 keys per user, duplicate prevention, status transitions

- [x] T027 [P] [US1] Implement PixKeyAudit entity in src/entities/pix_key_audit.py with:
  - Properties: audit_id, key_id, user_id, operation, timestamp, status, details
  - Events: REGISTERED, DEACTIVATED, REACTIVATED, DELETED, VALIDATION_FAILED

- [x] T028 [P] [US1] Create Pydantic schemas in src/models/pix_key_schemas.py:
  - RegisterPixKeyRequest (key_type, key_value, alias)
  - PixKeyResponse (key_id, key_type, key_value_masked, status, alias, validation_status, created_at, updated_at)
  - with field validators for CPF, email, phone formats

### Repository & Database Implementation for User Story 1

- [x] T029 [US1] Implement SQLAlchemy PixKey table in src/models/database_models.py with:
  - Columns: key_id, user_id, key_type, key_value_hash, key_value_masked, status, alias, is_preferred, validation_status, validation_error, pix_network_id, created_at, updated_at, revalidated_at
  - Constraints: unique(user_id, key_value_hash), check(status), check(key_type), FK(user_id → users)
  - Indexes: (user_id, status), (user_id, key_type), key_value_hash

- [x] T030 [US1] Implement SQLAlchemy PixKeyAudit table in src/models/database_models.py with:
  - Columns: audit_id, key_id, user_id, operation, timestamp, status, details (JSON)
  - FK(key_id → pix_keys.key_id)
  - Index: (user_id, timestamp desc)

- [ ] T031 [US1] Create database migration in migrations/versions/ for PixKey and PixKeyAudit tables
- [x] T032 [P] [US1] Implement SQLAlchemy PixKeyRepository in src/repositories/sqlalchemy_pix_key_repository.py:
  - Methods: create(), get_by_id(), get_by_user_id(), get_all_for_user(), update_status(), delete()
  - Find by hash with duplicate check
  - Count by user to enforce max 5 limit

- [x] T033 [P] [US1] Implement SQLAlchemy PixKeyAuditRepository in src/repositories/sqlalchemy_pix_key_audit_repository.py:
  - Method: create_audit_log(key_id, user_id, operation, status, details)
  - Method: get_audit_trail_for_key(key_id)

### Use Case Implementation for User Story 1

- [x] T034 [US1] Implement RegisterPixKeyUseCase in src/use_cases/register_pix_key.py:
  - Input: user_id, key_type, key_value (optional), alias (optional)
  - Validate key format based on key_type
  - Check for duplicates via repository
  - Check max 5 keys limit
  - Create PixKey entity
  - Hash key_value
  - Generate masked display
  - Save to database via repository
  - Create audit log entry
  - Return: PixKey with plaintext key_value (one-time display)
  - Raise: ValidationError, DuplicateKeyError, MaxKeysExceededError

### Controller & API Implementation for User Story 1

- [ ] T035 [US1] Create FastAPI router in src/api/pix_keys_router.py
- [ ] T036 [P] [US1] Implement POST /api/v1/pix-keys/register endpoint in src/api/pix_keys_router.py:
  - Route handler in PixKeyController
  - Extract user_id from auth middleware
  - Call RegisterPixKeyUseCase
  - Return 201 Created with PixKeyResponse (including plaintext key_value)
  - Handle exceptions → 400/409/429 responses
  - Log request/response with request_id

### Integration & Documentation for User Story 1

- [ ] T037 [US1] Register PixKeysRouter in main FastAPI app (src/main.py)
- [ ] T038 [P] [US1] Add OpenAPI documentation annotations to register endpoint (docstring with examples)
- [ ] T039 [US1] Run full test suite for US1 and verify 80%+ coverage for this story

**Checkpoint**: User Story 1 complete and testable independently. Users can register Pix Keys.

---

## Phase 4: User Story 2 - View Pix Keys (Priority: P1)

**Goal**: Users can retrieve all registered Pix Keys with status, type, and metadata

**Independent Test**: Can verify by registering one key and retrieving the list with correct metadata

### Tests for User Story 2 (TDD) 📝

- [ ] T040 [P] [US2] Unit test: ViewPixKeysUseCase in tests/unit/use_cases/test_view_pix_keys_use_case.py
  - Test retrieve all active keys
  - Test retrieve all keys (mixed status)
  - Test filter by status
  - Test filter by key_type
  - Test sorting by created_at, updated_at, key_type
  - Test pagination (page, limit)
  - Test empty list for user with no keys
  - Test masked key_value in response

- [ ] T041 [P] [US2] Contract test: GET /api/v1/pix-keys/list endpoint in tests/contract/test_view_pix_keys_endpoint.py
  - Test 200 response with key list
  - Test query params (status, key_type, sort_by, page, limit)
  - Test response structure (success, data, pagination)
  - Test 401 on missing auth
  - Test empty list response when no keys

- [ ] T042 [P] [US2] Integration test: List flow with multiple keys in tests/integration/test_view_pix_keys_flow.py
  - Test persistence (keys from DB appear in list)
  - Test filtering accuracy
  - Test sorting order
  - Test pagination boundaries

### Use Case Implementation for User Story 2

- [ ] T043 [US2] Implement ViewPixKeysUseCase in src/use_cases/view_pix_keys.py:
  - Input: user_id, filters (status, key_type), sort_by, page, limit
  - Retrieve keys via repository with filters
  - Apply sorting (created_at desc default)
  - Apply pagination
  - Return: List[PixKey] with masked values
  - Raise: InvalidFilterError

### Controller & API Implementation for User Story 2

- [ ] T044 [P] [US2] Implement GET /api/v1/pix-keys/list endpoint in src/api/pix_keys_router.py:
  - Query parameters: status, key_type, sort_by, page, limit
  - Call ViewPixKeysUseCase
  - Return 200 with paginated list response
  - Log query parameters and result count

- [ ] T045 [P] [US2] Implement GET /api/v1/pix-keys/{key_id} endpoint in src/api/pix_keys_router.py:
  - Get specific key by key_id
  - Verify user_id ownership
  - Return PixKeyResponse with masked value

### Schema & Documentation for User Story 2

- [ ] T046 [P] [US2] Create response schemas in src/models/pix_key_schemas.py:
  - PixKeyResponse with masked key_value
  - PixKeyListResponse with pagination (items, total, page, page_size)

- [ ] T047 [US2] Document list endpoint with example responses and filter options

**Checkpoint**: User Story 2 complete. Users can view all registered keys with filtering/sorting.

---

## Phase 5: User Story 3 - Deactivate Pix Key (Priority: P1)

**Goal**: Users can deactivate active Pix Keys to stop receiving payments through them

**Independent Test**: Register a key, deactivate it, verify status changes to INACTIVE

### Tests for User Story 3 (TDD) 📝

- [ ] T048 [P] [US3] Unit test: DeactivatePixKeyUseCase in tests/unit/use_cases/test_deactivate_pix_key_use_case.py
  - Test successful deactivation of active key
  - Test error when deactivating already inactive key
  - Test error when key not found
  - Test error when user not owner of key
  - Test is_preferred reset to false on deactivation
  - Test status transition validation

- [ ] T049 [P] [US3] Unit test: Activate/Reactivate in tests/unit/use_cases/test_activate_pix_key_use_case.py
  - Test successful reactivation of inactive key
  - Test error reactivating already active key

- [ ] T050 [P] [US3] Contract test: POST /api/v1/pix-keys/{key_id}/deactivate endpoint in tests/contract/test_deactivate_endpoint.py
  - Test 200 response on successful deactivation
  - Test 404 response on key not found
  - Test 403 response on unauthorized user
  - Test 409 response on invalid status transition
  - Test 401 on missing auth

- [ ] T051 [P] [US3] Integration test: Deactivation flow in tests/integration/test_deactivate_flow.py
  - Test DB update (status change in pix_keys table)
  - Test audit log entry creation (DEACTIVATED operation)
  - Test timestamp updates

### Entity & Use Case Implementation for User Story 3

- [ ] T052 [P] [US3] Add status transition methods to PixKey entity:
  - deactivate() → status ACTIVE→INACTIVE, reset is_preferred, update timestamp
  - activate() → status INACTIVE→ACTIVE, update timestamp
  - Validation: only allow valid transitions

- [ ] T053 [US3] Implement DeactivatePixKeyUseCase in src/use_cases/deactivate_pix_key.py:
  - Input: user_id, key_id
  - Retrieve key via repository
  - Verify user ownership
  - Validate status transition (must be ACTIVE)
  - Call key.deactivate()
  - Update in repository
  - Create audit log (DEACTIVATED operation)
  - Return: Updated PixKey
  - Raise: KeyNotFoundError, UnauthorizedError, InvalidStatusTransitionError

- [ ] T054 [P] [US3] Implement ActivatePixKeyUseCase in src/use_cases/activate_pix_key.py:
  - Input: user_id, key_id
  - Retrieve key via repository
  - Verify user ownership
  - Validate status transition (must be INACTIVE)
  - Call key.activate()
  - Update in repository
  - Create audit log (REACTIVATED operation)
  - Return: Updated PixKey

### Controller & API Implementation for User Story 3

- [ ] T055 [US3] Implement POST /api/v1/pix-keys/{key_id}/deactivate endpoint:
  - Extract user_id from auth
  - Call DeactivatePixKeyUseCase
  - Return 200 with updated PixKeyResponse
  - Handle exceptions → appropriate status codes

- [ ] T056 [P] [US3] Implement POST /api/v1/pix-keys/{key_id}/activate endpoint:
  - Extract user_id from auth
  - Call ActivatePixKeyUseCase
  - Return 200 with updated PixKeyResponse

### Documentation for User Story 3

- [ ] T057 [US3] Document deactivate/activate endpoints with operation sequences and error codes

**Checkpoint**: User Story 3 complete. Users can manage active/inactive status of keys.

---

## Phase 6: User Story 4 - Delete Pix Key (Priority: P2)

**Goal**: Users can permanently delete deactivated Pix Keys to keep list clean

**Independent Test**: Register, deactivate, delete, verify key no longer in list

### Tests for User Story 4 (TDD) 📝

- [ ] T058 [P] [US4] Unit test: DeletePixKeyUseCase in tests/unit/use_cases/test_delete_pix_key_use_case.py
  - Test successful deletion of inactive key
  - Test error when deleting active key
  - Test 404 when key not found
  - Test 403 when user not owner

- [ ] T059 [P] [US4] Contract test: DELETE /api/v1/pix-keys/{key_id} endpoint in tests/contract/test_delete_endpoint.py
  - Test 204 No Content on successful delete
  - Test 404 on key not found
  - Test 403 on unauthorized
  - Test 409 when key is active

- [ ] T060 [P] [US4] Integration test: Delete flow in tests/integration/test_delete_flow.py
  - Test DB deletion (key no longer in pix_keys table)
  - Test audit log persists after deletion
  - Test key not returned in list after deletion

### Use Case & Controller Implementation for User Story 4

- [ ] T061 [US4] Implement DeletePixKeyUseCase in src/use_cases/delete_pix_key.py:
  - Input: user_id, key_id
  - Retrieve key via repository
  - Verify user ownership
  - Validate status (must be INACTIVE)
  - Delete from repository
  - Create audit log (DELETED operation)
  - Raise: KeyNotFoundError, UnauthorizedError, CannotDeleteActiveKeyError

- [ ] T062 [P] [US4] Implement DELETE /api/v1/pix-keys/{key_id} endpoint:
  - Extract user_id from auth
  - Call DeletePixKeyUseCase
  - Return 204 No Content
  - Handle exceptions

**Checkpoint**: User Story 4 complete (P2).

---

## Phase 7: User Story 5 - Audit Trail Access (Priority: P3)

**Goal**: Users can view complete history of all changes to their Pix Keys

**Independent Test**: Verify audit trail shows all operations (register, deactivate, delete, etc.)

### Tests for User Story 5 (TDD) 📝

- [ ] T063 [P] [US5] Unit test: GetAuditTrailUseCase in tests/unit/use_cases/test_audit_trail_use_case.py
  - Test retrieve all audit entries for user
  - Test retrieve audit entries for specific key
  - Test filter by operation type
  - Test sorting by timestamp
  - Test pagination

- [ ] T064 [P] [US5] Contract test: GET /api/v1/pix-keys/{key_id}/audit-trail endpoint in tests/contract/test_audit_endpoint.py
  - Test 200 response with audit entries
  - Test query params (operation, sort, page, limit)
  - Test 404 when key not found
  - Test 403 on unauthorized user

- [ ] T065 [P] [US5] Integration test: Audit trail retrieval in tests/integration/test_audit_trail_flow.py
  - Test complete operation history tracking from add/update/delete
  - Test immutability of audit records

### Use Case & Controller Implementation for User Story 5

- [ ] T066 [US5] Implement GetAuditTrailUseCase in src/use_cases/get_audit_trail.py:
  - Input: user_id, key_id (optional), operation (optional), page, limit, sort_by
  - Retrieve audit entries via AuditRepository with filters
  - Apply sorting and pagination
  - Return: List[PixKeyAudit]

- [ ] T067 [P] [US5] Implement GET /api/v1/pix-keys/{key_id}/audit-trail endpoint:
  - Query params: operation, sort_by, page, limit
  - Call GetAuditTrailUseCase
  - Return 200 with paginated audit entries

- [ ] T068 [P] [US5] Create audit response schema in src/models/pix_key_schemas.py

**Checkpoint**: User Story 5 complete (P3).

---

## Phase N: Polish & Cross-Cutting Concerns

### Error Handling & Edge Cases

- [ ] T069 Comprehensive exception handling for all layers (domain, use case, controller)
- [ ] T070 [P] Standard error response format across all endpoints
- [ ] T071 [P] Validation error messages with field-level details
- [ ] T072 Concurrency handling: Test simultaneous operations (race condition tests)
- [ ] T073 [P] Input sanitization and security validation (SQL injection, XSS prevention)

### Testing Coverage & Quality

- [ ] T074 Verify 80%+ code coverage across all modules
- [ ] T075 [P] Run mypy type checking with strict mode
- [ ] T076 [P] Run Ruff linter and Black formatter on entire codebase
- [ ] T077 [P] Run full test suite (unit + integration + contract tests)
- [ ] T078 Performance testing: Verify <100ms p95 latency for key operations
- [ ] T079 Load testing: Verify system handles 1000 req/s (optional for MVP)

### Documentation & API

- [ ] T080 Add OpenAPI/Swagger documentation for all endpoints
- [ ] T081 [P] Create API usage examples in swagger/README.md
- [ ] T082 [P] Document error codes and their meanings
- [ ] T083 [P] Create architecture diagram (entities, use cases, controllers)
- [ ] T084 Document deployment procedures

### Database & Data Integrity

- [ ] T085 Test database constraints (foreign keys, unique constraints, checks)
- [ ] T086 [P] Test cascade behaviors and data consistency
- [ ] T087 Create database backup/restore procedures
- [ ] T088 Verify indexes exist and query performance with EXPLAIN plans

### Observability & Monitoring

- [ ] T089 Verify JSON structured logging in all layers
- [ ] T090 [P] Test logging output format (request_id, operation, duration, outcome)
- [ ] T091 Create log aggregation examples (ELK, Datadog, etc.)
- [ ] T092 [P] Add application metrics (request count, latency histograms)

### Deployment & Configuration

- [ ] T093 Create Docker container for service (Dockerfile, requirements.txt)
- [ ] T094 [P] Create docker-compose.yml for local development (app + PostgreSQL)
- [ ] T095 Create environment configuration templates (.env.example)
- [ ] T096 [P] Setup CI/CD pipeline (GitHub Actions) for automated testing
- [ ] T097 Create deployment guide (production checklist)

### Final Validation

- [ ] T098 End-to-end testing: Complete user journey (register → view → deactivate → delete → audit)
- [ ] T099 [P] Manual testing checklist against all acceptance scenarios from spec.md
- [ ] T100 Code review checklist: Constitution compliance, test coverage, documentation
- [ ] T101 Prepare release notes and feature documentation

---

## Summary

**Total Tasks**: 101  
**Parallelizable Tasks**: ~35 marked with [P]  
**Suggested Phases**: 7 sequential phases + Polish phase  
**Estimated Timeline**: 
- Phase 1 (Setup): 1 day
- Phase 2 (Foundation): 2-3 days
- Phase 3 (US1): 2-3 days
- Phase 4 (US2): 1-2 days
- Phase 5 (US3): 1-2 days
- Phase 6 (US4): 1 day (P2)
- Phase 7 (US5): 1 day (P3)
- Polish: 2-3 days

**MVP Scope** (P1 Only): Phases 1-5 (Core registration, viewing, deactivation functionality)  
**P2/P3 Scope**: Optional phases with deletion, notifications, audit trail

---

## Testing Strategy Summary

**Test Pyramid**:
- **Unit Tests** (60%): Entity validation, use case logic, validators
- **Integration Tests** (25%): Database persistence, full use case flows, audit logging
- **Contract/API Tests** (15%): HTTP endpoints, error handling, response formats

**Minimum Coverage**: 80% per module  
**Test-First Approach**: Every task MUST have tests written and failing before implementation

---

## Dependencies Map

```
Phase 2 (Foundation) - BLOCKING ALL USER STORIES
    ↓
Phase 3 (US1 - Register) - Can proceed after Phase 2
Phase 4 (US2 - View) - Depends on Phase 3 (needs keys to view)
Phase 5 (US3 - Deactivate) - Depends on Phase 3
Phase 6 (US4 - Delete) - Depends on Phase 5 (must deactivate first)
Phase 7 (US5 - Audit) - Independent of uses cases, just reads audit log
    ↓
Phase N (Polish) - All implementations complete before polish
```

Suggested execution: Complete Phase 2 first, then run Phases 3-7 with focused parallelization within each phase (tasks marked [P] can run in parallel).
