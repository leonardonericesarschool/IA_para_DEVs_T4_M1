# Implementation Plan: Pix Keys Management

**Branch**: `001-manage-pix-keys` | **Date**: 2026-04-22 | **Spec**: [specs/001-manage-pix-keys/spec.md](spec.md)
**Input**: Feature specification from `/specs/001-manage-pix-keys/spec.md`

## Summary

Users need a centralized application to register, view, and manage their Pix Keys (CPF, email, phone, or random identifiers) to receive instant payments through the Brazilian Pix payment system. This MVP delivers core key management functionality (register, view, deactivate/reactivate) with clean architecture layering, comprehensive validation, and audit trails for compliance. Service will follow Python Clean Code Architecture with strict layer separation (Entities → Use Cases → Controllers → Frameworks), test-first development (80% coverage target), dependency injection for loose coupling, and repository pattern for data abstraction.

## Technical Context

**Language/Version**: Python 3.9+  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0+, Pydantic v2, pytest  
**Storage**: PostgreSQL with 4 tables (pix_keys, pix_key_audits, pix_key_validations, users)  
**Testing**: pytest with pytest-cov (80% coverage target), pytest-asyncio for async tests  
**Target Platform**: Linux/cloud-native web service (FastAPI async)
**Project Type**: Web service (REST API backend)  
**Performance Goals**: <100ms p95 latency for key operations, handle 1000 req/s  
**Constraints**: User must not see plaintext keys except once at registration; all keys must be validated before activation; max 5 keys per user account  
**Scale/Scope**: MVP P1-P3 (6 user stories), 4 domain entities, 8 API endpoints, 3 main use cases for P1

## Constitution Check

**Gate Analysis**: Python Web Services Clean Code Architecture Constitution

### Pre-Design Verification ✅
| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| **Clean Code Architecture** | Layer separation: Entities → Use Cases → Controllers → Frameworks | ✅ PASS | Design includes 4-layer structure (see quickstart.md) |
| **Test-First Development** | Mandatory TDD with 80%+ coverage | ✅ PASS | Test strategy documented; TDD workflow required |
| **Dependency Injection** | All dependencies injected, no direct instantiation | ✅ PASS | Use case injection pattern specified |
| **Repository Pattern** | Database access only through repositories | ✅ PASS | PixKeyRepository abstract interface with SQLAlchemy impl |
| **Observability** | Structured JSON logging with request_id | ✅ PASS | Audit trail + JSON logging documented |

### Design Alignment ✅
- ✅ Entities layer: PixKey, PixKeyValidator, PixKeyAudit (business logic independent of framework)
- ✅ Use Cases layer: RegisterPixKeyUseCase, DeactivatePixKeyUseCase (orchestrate workflows)
- ✅ Controllers layer: PixKeyController (HTTP handlers, request/response mapping)
- ✅ Frameworks layer: FastAPI routes, SQLAlchemy ORM (interchangeable without business logic change)
- ✅ Repository abstraction: PixKeyRepository ABC + SQLAlchemy implementation
- ✅ Error handling: Domain exceptions (business rules) → Application exceptions (use case failures)
- ✅ Data validation: Pydantic schemas + entity validation rules

### No Violations ✅
All Constitutional principles satisfied. No deviations requiring complexity tracking.

## Project Structure

### Documentation (this feature)

```text
specs/001-manage-pix-keys/
├── plan.md              # Implementation plan (this file)
├── spec.md              # Feature specification
├── research.md          # Phase 0: Research & clarifications (✅ COMPLETE)
├── data-model.md        # Phase 1: Domain entities & schema
├── quickstart.md        # Phase 1: Architecture overview & guides
├── contracts/           # Phase 1: API contracts
│   └── api-contracts.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/
├── pix_keys/
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── pix_key.py              # PixKey domain entity
│   │   ├── pix_key_validator.py    # Validation rules (CPF/email/phone/random)
│   │   └── pix_key_audit.py        # Audit trail entity
│   │
│   ├── use_cases/
│   │   ├── __init__.py
│   │   ├── register_pix_key.py     # RegisterPixKeyUseCase
│   │   ├── view_pix_keys.py        # ViewPixKeysUseCase
│   │   ├── deactivate_pix_key.py   # DeactivatePixKeyUseCase
│   │   ├── activate_pix_key.py     # ActivatePixKeyUseCase
│   │   ├── edit_pix_key.py         # EditPixKeyUseCase (P2)
│   │   └── delete_pix_key.py       # DeletePixKeyUseCase (P2)
│   │
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── pix_key_controller.py   # FastAPI HTTP handlers
│   │
│   ├── gateways/
│   │   ├── __init__.py
│   │   ├── pix_network_gateway.py  # Pix network validation (stub for P2)
│   │   └── audit_log_gateway.py    # Audit trail persistence
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── pix_key_repository.py   # Abstract repository interface (ABC)
│   │   └── sqlalchemy_pix_key_repository.py  # SQLAlchemy implementation
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── pydantic_schemas.py     # Request/response Pydantic models
│   │
│   ├── exceptions/
│   │   ├── __init__.py
│   │   ├── domain_exceptions.py    # Business rule violations
│   │   └── application_exceptions.py  # Use case failures
│   │
│   └── config.py                   # DI container & FastAPI setup

tests/
├── unit/
│   ├── entities/
│   │   ├── test_pix_key.py
│   │   ├── test_pix_key_validator.py
│   │   └── test_pix_key_audit.py
│   │
│   └── use_cases/
│       ├── test_register_pix_key.py
│       ├── test_view_pix_keys.py
│       ├── test_deactivate_pix_key.py
│       └── test_activate_pix_key.py
│
├── integration/
│   ├── test_pix_key_repository.py
│   ├── test_sqlalchemy_pix_key_repository.py
│   └── test_pix_key_controller.py
│
└── contract/
    └── test_api_contracts.py

requirements.txt       # Python dependencies
.env.example          # Configuration template
conftest.py           # pytest fixtures
```

**Structure Decision**: Single project with standard Python web service layout. Implements Clean Code Architecture with clear layer boundaries:
1. **Entities**: Domain models (PixKey, PixKeyValidator) with business logic
2. **Use Cases**: Application workflows orchestrating entity operations
3. **Controllers**: HTTP handlers (FastAPI routes) mapping requests to use cases
4. **Repositories**: Abstract data access (PixKeyRepository ABC) with SQLAlchemy implementation
5. **Exceptions**: Hierarchy for domain → application → infrastructure errors

This structure enables independent layer testing, clear separation of concerns, and framework replacement without business logic changes (e.g., replace FastAPI with Flask).

## Complexity Tracking

**Status**: No Constitution violations. All design principles satisfied without trade-offs.

The implementation follows all Constitutional requirements without exceptions:
- ✅ Clean Code Architecture layers strictly enforced
- ✅ Test-First Development (TDD) mandatory
- ✅ Dependency Injection throughout
- ✅ Repository Pattern for data access
- ✅ Structured logging & observability

No complexity justification needed. Ready for implementation phase.

---

## Implementation Roadmap

### Phase 1: Entities Layer (Week 1)
- [ ] Create PixKey domain entity with validation rules
- [ ] Implement PixKeyValidator (CPF, email, phone, random formats)
- [ ] Create PixKeyAudit entity for audit trail
- [ ] Write 80+ unit tests for entities
- [ ] Define exception hierarchy

### Phase 2: Use Cases Layer (Week 2)
- [ ] Implement RegisterPixKeyUseCase
- [ ] Implement ViewPixKeysUseCase
- [ ] Implement DeactivatePixKeyUseCase
- [ ] Implement ActivatePixKeyUseCase
- [ ] Write use case integration tests

### Phase 3: Interface Adapters (Week 3)
- [ ] Design PixKeyRepository abstraction (ABC)
- [ ] Implement SQLAlchemy repository
- [ ] Create Pydantic request/response schemas
- [ ] Implement PixKeyController (FastAPI routes)
- [ ] Write integration tests for repository & controller

### Phase 4: Frameworks Setup (Week 4)
- [ ] Configure FastAPI application
- [ ] Setup PostgreSQL migrations
- [ ] Implement DI container
- [ ] Add structured JSON logging
- [ ] Deploy to test environment

### Phase 5: Testing & Review (Week 5)
- [ ] End-to-end testing of all P1 workflows
- [ ] Code review against Constitution
- [ ] Performance testing (<100ms p95)
- [ ] Security review (key masking, hashing)
- [ ] Merge to main branch

### Phase 6: P2 Features (Sprint 2)
- [ ] Implement EditPixKeyUseCase
- [ ] Implement DeletePixKeyUseCase
- [ ] Add search/filter functionality
- [ ] Implement PixKey validation with Pix network stub

---

## Generated Artifacts

✅ **Phase 0 Complete**:
- [research.md](research.md) - All clarifications resolved

✅ **Phase 1 Complete**:
- [data-model.md](data-model.md) - Entity definitions & schema
- [contracts/api-contracts.md](contracts/api-contracts.md) - API specification
- [quickstart.md](quickstart.md) - Architecture overview & test strategy

✅ **Phase 2 (This Plan)**:
- [plan.md](plan.md) - Implementation roadmap

📋 **Next Phase (Phase 2: Tasks)**:
- Will generate: `/speckit.tasks` command output
- Contains: Granular implementation tasks with acceptance criteria

---

## Sign-Off

**Design Review**: ✅ APPROVED

This implementation plan aligns with:
- ✅ Feature specification (spec.md)
- ✅ Python Web Services Constitution
- ✅ Clean Code Architecture principles
- ✅ Test-First Development requirements
- ✅ Repository Pattern for data abstraction
- ✅ Dependency Injection for loose coupling

**Status**: Ready for implementation phase. All design gates passed.

**Next Command**: `speckit.tasks` to generate granular implementation tasks with acceptance criteria.

