# Research & Clarifications: Pix Keys Management Feature

**Date**: 2026-04-22  
**Feature**: Pix Keys Management (MVP P1-P3)  
**Status**: Complete - All NEEDS CLARIFICATION resolved

---

## Clarification 1: Failed Payment Handling & Notifications

### Question
User Story 3, Scenario 4: "When someone attempts to send money to that identifier, the system rejects the payment (via Pix network) and the transaction fails. How do we handle failed payments and notify users about attempted payments?"

### Research & Decision

**Context**: The Pix system (Central Bank of Brazil) operates as a real-time payment network. When a payment is attempted to an inactive key, the Pix infrastructure itself rejects the request at the routing layer before it reaches the user's bank.

**Decision**: 
- **Rejection Handling**: The system does NOT need to actively reject payments. The Pix network itself enforces this at infrastructure level. When a key is deactivated, it remains registered in the Pix network but marked as "inactive" status. The Pix routing system will reject any incoming payments to inactive keys with a "Chave Não Ativa" (Key Not Active) response.
- **User Notification**: The application is NOT responsible for notifying users of failed payment attempts from external parties. This is handled by:
  1. The sender's bank (provides feedback to the sender when payment is rejected)
  2. The user's bank (may send transaction denial notification if configured)
  3. Pix transaction history (users can check their Pix transaction log at their bank)
- **Application Scope**: The application focuses on key status management. If required in P2, audit logs can track key activations/deactivations for compliance, but real-time payment attempt notifications are out of scope for MVP.

**Rationale**: Aligns with centralized Pix infrastructure model where payment routing is handled at network level, not at individual service level. Reduces system complexity and eliminates need for webhooks/callbacks from Pix network.

**Alternatives Considered**:
1. Build webhook listener for payment rejections → Rejected: Pix network doesn't provide per-service webhooks; only aggregate transaction reporting
2. Poll transaction history → Rejected: Adds complexity and latency; real-time detection impossible
3. User opt-in notifications → Rejected: MVP scope is key management only; notifications are P2+ feature

---

## Clarification 2: Default Notification Mechanism & User Preferences

### Question
User Story 5, Scenario 2: "When a user marks one key as 'preferred' for notifications, how are notifications delivered and what preferences are available?"

### Research & Decision

**Context**: The specification mentions a "preferred" flag for keys but doesn't define how notifications use this. The MVP scope is key management, not full notification system.

**Decision for MVP**:
- **Preferred Key Flag**: Store as boolean field in PixKey entity (is_preferred)
- **Initial Use Case**: Reserved for future use in notification system (P2+). In MVP, the flag exists for data model completeness and future features
- **User Preferences**: Deferred to P2. MVP does NOT implement notification delivery; only stores the preference metadata
- **Implementation**: 
  - Allow users to mark one key as preferred via edit UI
  - Enforce constraint: only one key per user can be marked is_preferred=true at a time
  - This preference has no functional impact in MVP; it's ready for P2 notification features

**Rationale**: Separates concerns. Key management (P1) is independent of notification delivery (P2). Data model is future-proof without building unnecessary notification infrastructure now.

**Alternatives Considered**:
1. Build full notification system in P1 → Rejected: Out of MVP scope, requires additional dependencies (email/SMS gateways)
2. Remove preference flag from P1 → Rejected: Creates data migration work in P2; building it now costs nothing
3. Default to random key selection → Rejected: User experience suffers; explicit preference better

---

## Clarification 3: Maximum Pix Keys Per User Account

### Question
Edge Cases: "What is the maximum number of Pix Keys per user account?"

### Research & Decision

**Technical Context**: Pix regulations and practical limits:
- **Legal Maximum**: Brazilian Central Bank allows up to 5 keys per account (Resolution BCB #32/2020)
- **Technical Maximum**: No technical constraint; ORM handles arbitrary number
- **UX Consideration**: Managing >5 keys becomes challenging for users; 5 is established best practice

**Decision**: 
- **Maximum**: 5 Pix Keys per user account
- **Enforcement**: Application-level validation in registration use case
- **Error Handling**: When user attempts to register 6th key, display: "You have reached the maximum number of Pix Keys (5). Delete or deactivate unused keys to register new ones."
- **Rationale for Choice**: Aligns with legal maximum, supports practical user workflows, prevents abuse

**Alternatives Considered**:
1. No limit (unlimited) → Rejected: Violates BCB regulations; creates performance and UX issues
2. 10 keys → Rejected: Exceeds BCB limit; not legally compliant
3. 3 keys → Rejected: Too restrictive; users often need multiple payment methods

---

## Clarification 4: Pix Network Validation API Integration

### Question
Technical: What validation API does the system use for Pix key validation?

### Research & Decision

**Context**: Brazilian Pix ecosystem offers validation through SPB (Sistema de Pagamentos Brasileiros) DICT API or bank-specific APIs. 

**Decision**:
- **Validation Method**: Application validates against local formatting rules (CPF, email, phone) and maintains a pending status for keys awaiting network validation
- **Network Validation**: Validation with Pix network happens at integration time (P2). MVP stores validation_status field but does NOT require external API calls during registration
- **Format Validation Rules**:
  - **CPF**: 11 digits, valid check digit per CPF algorithm (DNI validation)
  - **Email**: Valid email format (RFC 5322 simplified), domain exists
  - **Phone**: 11 digits (mobile) or 10 digits (landline), valid area code (DDD valid in Brazil)
  - **Random**: UUID4 with "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx" format

**Rationale**: MVP focuses on registration and status management. Network validation is deferred to P2 integration phase where actual SPB/DICT connectivity is established.

**Alternatives Considered**:
1. Synchronous SPB DICT API calls → Rejected for MVP: Adds external dependency; SPB API may have rate limits
2. Async validation queue → Rejected for MVP: Adds complexity; simple synchronous validation sufficient
3. Bank-specific validation → Rejected for MVP: User's bank is not tracked in MVP; deferred to P2

---

## Clarification 5: Project Architecture & Technology Stack

### Question
Technical: What is the assumed technology stack and project structure?

### Research & Decision

**Decision** (Aligned with Constitution - Python Web Services Clean Code Architecture):

**Language & Framework**:
- Python 3.9+ (per Constitution)
- FastAPI for web service (async capability for high-throughput)
- SQLAlchemy 2.0+ for ORM with async support
- PostgreSQL for persistent storage

**Project Structure**:
```
src/
├── entities/           # Domain models: User, PixKey, PixKeyAudit, PixKeyValidation
├── use_cases/          # Application logic: RegisterPixKeyUseCase, DeactivatePixKeyUseCase, etc.
├── controllers/        # HTTP handlers: PixKeyController (FastAPI routes)
├── gateways/           # External integration: PixNetworkGateway (stub for P2), AuditLogGateway
├── repositories/       # Data access: PixKeyRepository (ABC + SQLAlchemy impl)
├── validators/         # Business logic: PixKeyValidator (format + business rules)
└── config.py           # Configuration & dependency injection setup

tests/
├── unit/               # Entity & use case tests (80% target)
├── integration/        # Repository & gateway tests
└── contract/           # API contract tests
```

**Justification**: Layers aligned with Constitution:
1. **Entities**: Core Pix key domain logic (validation rules, state transitions)
2. **Use Cases**: Registration, deactivation, viewing workflows
3. **Controllers**: FastAPI routes handling HTTP concerns
4. **Gateways**: Pix network stub (ready for P2 integration)
5. **Repositories**: Abstract database access behind protocol

**Rationale**: Enables independent component testing, loose coupling, and future refactoring without business logic changes.

**Dependencies** (Approved by Constitution):
- FastAPI (web framework)
- SQLAlchemy (ORM)
- Pydantic (request/response validation)
- pytest + pytest-cov (testing)
- python-json-logger (JSON logging)

---

## Clarification 6: Authentication & Authorization Scope

### Question
Technical: What authentication/authorization is assumed for the feature?

### Research & Decision

**Decision** (from spec Assumption #1):
- **MVP Assumption**: User authentication already exists (user_id provided by auth middleware)
- **Authorization**: Users can ONLY access/manage their own keys; no cross-user access
- **Admin Features**: No admin override or key management on behalf of other users (P2+ feature)
- **Implementation**: Use dependency injection to pass user_id from request context to use cases

**Rationale**: Focuses MVP on core key management. Authentication/authorization frameworks are handled by outer layer (auth middleware) and injected into use cases.

**Security Note**: Ensures every repository query filters by user_id to prevent cross-user data access.

---

## Clarification 7: Audit & Compliance Logging

### Question
Technical: What audit trail format and retention policy is required?

### Research & Decision

**Decision**:
- **Audit Events**: Log every key lifecycle event (register, activate, deactivate, delete, revalidate)
- **Audit Data**: event_type, key_id, user_id, timestamp, details (e.g., old_status → new_status)
- **Format**: JSON structured logging (python-json-logger) with request_id for traceability
- **Retention**: Deferred to P2 (infrastructure decision); MVP stores indefinitely
- **Compliance**: Audit table enables CB audits and LGPD compliance (user can request export of their key history)

**Implementation**:
```python
# Audit entry structure
{
  "timestamp": "2026-04-22T10:30:00Z",
  "event_type": "key_registered",  # registered|activated|deactivated|deleted|revalidated
  "key_id": "uuid",
  "user_id": "uuid",
  "details": {
    "key_type": "email",
    "key_value_hash": "sha256(key)",  # Never store plaintext
    "alias": "Work Email"
  },
  "request_id": "uuid"
}
```

---

## Clarification 8: Data Masking & Security

### Question
Technical: How much of the key should be revealed in UI and logs?

### Research & Decision

**Decision**:
- **Registration Confirmation**: Show full key once after successful registration, prompt to save
- **List View**: Masked display
  - Email: "user***@example.com"
  - Phone: "11 9****-****"
  - CPF: "***.***.***-**"
  - Random: Show full UUID (not sensitive)
- **Audit Logs**: Hash the key value (SHA-256) never store plaintext
- **API Responses**: Never include full key in API responses; only key_type, masked_value, status, metadata
- **Rationale**: Provides enough info for user to identify their keys without exposing full data if logs/databases are compromised

---

## Summary of Decisions

| Topic | Decision | Status |
|-------|----------|--------|
| Failed payment handling | Handled by Pix network infrastructure; user notifications out of scope for MVP | ✅ Resolved |
| Notification preferences | Preferred flag stored; notifications deferred to P2 | ✅ Resolved |
| Max keys per account | 5 keys (BCB limit) | ✅ Resolved |
| Validation approach | Local format validation; network validation P2 | ✅ Resolved |
| Stack | Python 3.9+, FastAPI, SQLAlchemy, PostgreSQL | ✅ Resolved |
| Architecture | Clean Code Architecture with 4 layers | ✅ Resolved |
| Auth scope | User_id from middleware; no admin override in MVP | ✅ Resolved |
| Audit logging | JSON structured logs with event tracking | ✅ Resolved |
| Data masking | Masked display in UI; hash in logs | ✅ Resolved |

All NEEDS CLARIFICATION markers from spec.md have been addressed. Ready to proceed to Phase 1: Design & Architecture.
