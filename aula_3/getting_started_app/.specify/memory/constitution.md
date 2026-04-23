<!-- SYNC IMPACT REPORT
Version: 1.0.0 (NEW)
Rationale: Initial constitution creation for Python web services with Clean Code Architecture
Principles Added: 5 core principles + Technical Stack + Development Workflow sections
Templates Updated: plan-template.md, spec-template.md, tasks-template.md, commands (pending manual review)
TODO: Review dependent templates for alignment with architecture layers and testing requirements
-->

# Python Web Services Constitution
Building web services in Python with Clean Code Architecture principles and best practices.

## Core Principles

### I. Clean Code Architecture
Every service MUST follow Clean Code Architecture with strict layer separation. Code organized into four independent layers:
- **Enterprise Business Rules** (Entities): Core domain models and business logic, independent of frameworks
- **Application Business Rules** (Use Cases): Service/interactor classes orchestrating workflows
- **Interface Adapters** (Controllers, Gateways): HTTP endpoints and external system integrations
- **Frameworks & Drivers** (FastAPI, SQLAlchemy, etc.): Technology-specific implementations replaceable without business logic changes

Layers depend inward only; inner layers never reference outer layers. Each layer has clear boundaries with tested contracts.

### II. Test-First Development (NON-NEGOTIABLE)
Test-Driven Development is MANDATORY. Workflow: Write tests → Get stakeholder approval → Tests fail → Implement → Tests pass → Refactor.
All code requires unit tests (minimum 80% coverage). Integration tests required for:
- Repository/database layer contracts
- Use case workflows involving multiple entities  
- API endpoint behavior and error handling
- Third-party service integrations

Tests serve as executable documentation; test names describe business intent, not implementation.

### III. Dependency Injection & Loose Coupling
All dependencies injected, never instantiated within business logic. Constructor injection preferred; factories for complex creation.
No direct imports of concrete implementations; use protocols/interfaces. Database clients, external APIs, configuration all injected.
Enables rapid testing (swap implementations), refactoring (replace implementations without code changes), and independent layer testing.

### IV. Repository Pattern & Data Abstraction
Database access ONLY through Repository interfaces. Repositories abstract:
- SQL queries and ORM details
- Connection management
- Transaction handling
- Query optimization decisions

Repository implementations hidden behind protocol/ABC interfaces. Business logic never references database structure directly.
Makes switching between SQL, NoSQL, or mock implementations trivial for testing.

### V. Observability & Error Handling
Structured logging (JSON format) required in all layers. Logs include: request ID, user context, operation, duration, outcome.
Exception hierarchy clearly defined: Domain exceptions (business rule violations), Application exceptions (use case failures),
Infrastructure exceptions (database, network). HTTP responses map exceptions to appropriate status codes with safe error messages.
Never expose internal implementation details in API responses.

## Technical Stack Requirements

**Language**: Python 3.9+
**Web Framework**: FastAPI (async/await) or Flask (for simpler services)
**ORM**: SQLAlchemy 2.0+ with async support
**Database**: PostgreSQL (primary), MySQL 8.0+ (if required), SQLite (development only)
**Testing**: pytest with pytest-cov, pytest-asyncio for async tests
**DI Container**: Dependency Injector library (or manual injection for simpler services)
**Logging**: Python logging with JSON formatter (python-json-logger)
**Validation**: Pydantic v2 for request/response serialization
**API Documentation**: OpenAPI/Swagger (automatic via FastAPI)
**Code Quality**: Black (formatting), Ruff (linting), mypy (type checking)

## Development Workflow & Code Review

**Branch Strategy**: Feature branches from main; conventional commits (feat:, fix:, test:, etc.)

**Code Review Gates**:
- All tests passing (unit + integration)
- Type checking (mypy) passing without # type: ignore comments
- Code coverage not decreasing
- New public APIs documented with docstrings + examples
- All review comments addressed before merge
- Squash commits before merge to maintain history clarity

**Dependency Management**: 
- requirements.txt or pyproject.toml with pinned versions
- Weekly automated security vulnerability checks
- No dependencies without clear justification and maintenance status check

**Database Changes**:
- Migrations must be backward compatible
- Rollback tested before deployment
- Migration files include documentation of intent

## Governance

This Constitution supersedes all other development practices and decisions. All team members must verify compliance
in code review. When tension arises between layers or principles, the inner-most layer winning rule applies: 
never compromise core business logic for outer layer convenience.

**Amendments**:
- Proposals must include rationale and impact analysis on existing code
- Require unanimous team agreement and documented migration plan if existing code must change
- Version updated using semantic versioning (MAJOR: incompatible principle changes, MINOR: new guidance, PATCH: clarifications)
- Amendment date recorded; all active development must comply within one sprint

**Compliance Verification**:
- Code review checklists align with these principles
- Architecture Decision Records (ADRs) required for any principle deviation
- Quarterly architecture reviews to assess real-world adherence
- Tools (mypy, Ruff, tests) configured to enforce requirements automatically

---

**Version**: 1.0.0 | **Ratified**: 2026-04-22 | **Last Amended**: 2026-04-22
