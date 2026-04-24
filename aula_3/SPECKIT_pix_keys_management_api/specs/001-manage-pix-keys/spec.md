# Feature Specification: Pix Keys Management App

**Feature Branch**: `001-manage-pix-keys`  
**Created**: 2026-04-22  
**Status**: Draft  
**Input**: User description: "I want to build an app to manage user Pix Keys."

## Overview

Users need a centralized application to register, view, update, and manage their Pix Keys (CPF, email, phone, or random identifiers) that enable them to receive instant payments through the Brazilian Pix payment system. This app serves as the control center for users to organize multiple Pix Keys and ensure they can receive payments through various channels.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register a Pix Key (Priority: P1)

A user wants to register a new Pix Key (CPF, email, phone number, or generate a random key) so they can receive payments through that identifier on the Pix network.

**Why this priority**: Core MVP requirement. Without the ability to register keys, the app provides no value. This is the foundational feature that enables all other workflows.

**Independent Test**: Can be fully tested by a user completing the registration flow for a single Pix Key type and verifying it appears in their key list with "active" status. Delivers complete value for one payment receiving method.

**Acceptance Scenarios**:

1. **Given** a user is on the key registration form, **When** they enter a valid CPF and submit, **Then** the system registers the key, displays a confirmation message, and the key appears in the user's key list as "active" and ready for use
2. **Given** a user is on the key registration form, **When** they enter a valid email address and submit, **Then** the system registers the key, displays a confirmation message, and the key appears in the user's key list as "active"
3. **Given** a user is on the key registration form, **When** they enter a valid phone number and submit, **Then** the system registers the key, displays a confirmation message, and the key appears in the user's key list as "active"
4. **Given** a user wants to use a random identifier, **When** they request a random key generation, **Then** the system generates a unique random Pix Key, displays it to the user, and registers it as "active"
5. **Given** a user submits an invalid Pix Key (e.g., malformed email, invalid CPF), **When** the system validates the input, **Then** it displays a clear error message explaining the issue and prevents registration

---

### User Story 2 - View Registered Pix Keys (Priority: P1)

A user wants to see all their registered Pix Keys with current status, type, and creation date so they know what payment identifiers are active.

**Why this priority**: Critical for MVP. Users need visibility into their registered keys to confirm their setup and choose which key to use for payments. Without this, users cannot verify their registration worked.

**Independent Test**: Can be fully tested by registering one key and viewing it in the list with correct metadata (type, status, creation date). Demonstrates that data persistence and retrieval work correctly.

**Acceptance Scenarios**:

1. **Given** a user has registered one or more Pix Keys, **When** they navigate to their key list, **Then** the system displays all registered keys with type (CPF/Email/Phone/Random), current status, and creation date in a clear, organized format
2. **Given** a user has no registered keys, **When** they navigate to the key list, **Then** the system displays an empty state message with a call-to-action to register their first key
3. **Given** a user is viewing their key list, **When** they look at the key display, **Then** the system shows only non-sensitive key information (e.g., email but masked CPF) to allow users to confirm identity without exposing full details

---

### User Story 3 - Deactivate a Pix Key (Priority: P1)

A user wants to deactivate a Pix Key they no longer wish to use for receiving payments, so their contacts cannot send money to that identifier.

**Why this priority**: Critical for MVP. Users must be able to control which keys are active; lack of deactivation creates security/usability issues. This is essential for managing their payment channels.

**Independent Test**: Can be fully tested by registering a key, deactivating it, and verifying its status changes to "inactive" and cannot receive payments. No impact on other keys.

**Acceptance Scenarios**:

1. **Given** a user has an active Pix Key, **When** they select the deactivate action and confirm, **Then** the system updates the key status to "inactive", displays a confirmation, and the key immediately stops receiving payments
2. **Given** a user deactivates a Pix Key, **When** they view their key list, **Then** the deactivated key is still visible but clearly marked as "inactive" so they can reactivate if needed
3. **Given** a user wants to deactivate a key, **When** they attempt the action, **Then** the system displays a confirmation dialog explaining the consequence and requesting confirmation before proceeding
4. **Given** a Pix Key is inactive, **When** someone attempts to send money to that identifier, **Then** the system rejects the payment (via Pix network) and the transaction fails [NEEDS CLARIFICATION: handling of failed payments and notifications to user about attempted payments]

---

### User Story 4 - Delete a Pix Key (Priority: P2)

A user wants to permanently remove a Pix Key from their account after deactivating it, to keep their key list clean and managed.

**Why this priority**: Important but not critical for MVP. Users can deactivate unwanted keys; permanent deletion is a convenience feature and can be implemented after initial release.

**Independent Test**: Can be fully tested by registering a key, deactivating it, deleting it, and verifying it no longer appears in the list.

**Acceptance Scenarios**:

1. **Given** a user has a deactivated Pix Key, **When** they select the delete action and confirm, **Then** the system permanently removes the key from the account and it no longer appears in the key list
2. **Given** an active Pix Key exists, **When** a user attempts to delete it, **Then** the system requires the user to deactivate it first before allowing deletion
3. **Given** a user deletes a key, **When** they view their key list, **Then** the key does not appear and cannot be recovered (it has been permanently deleted)

---

### User Story 5 - Edit Pix Key Details (Priority: P2)

A user wants to update metadata for a registered Pix Key (e.g., add an alias/nickname, set preferred key for notifications) to customize and organize their payment identifiers.

**Why this priority**: Valuable for user experience and organization but not essential for basic MVP. Adding a nickname or preferred flag improves usability and can be implemented after P1 features.

**Independent Test**: Can be fully tested by registering a key, adding an alias, and verifying it displays with that alias in the list.

**Acceptance Scenarios**:

1. **Given** a user has a registered Pix Key, **When** they open the edit form and add an alias (nicknamed "Work Email" for a @company.com email), **Then** the system updates the key metadata and displays the alias alongside the key in the list
2. **Given** a user with multiple keys, **When** they mark one key as "preferred" for notifications, **Then** the system marks that key with an indicator and uses it as the default for notification delivery [NEEDS CLARIFICATION: default notification mechanism and user preferences for delivery]
3. **Given** a user edits a key's metadata, **When** they save changes, **Then** the system updates the key without affecting its active/inactive status or receiving capabilities

---

### User Story 6 - Search and Filter Pix Keys (Priority: P3)

A user with many Pix Keys wants to search or filter by type (CPF/Email/Phone/Random) or status to quickly find specific keys.

**Why this priority**: Nice-to-have feature for users with many keys. Basic list view works for MVP; searching/filtering enhances usability for power users and can be deferred.

**Independent Test**: Can be fully tested by registering multiple keys of different types and filtering by type to verify correct results are shown.

**Acceptance Scenarios**:

1. **Given** a user has multiple Pix Keys, **When** they use a filter to show only email-based keys, **Then** the system displays only keys registered with email addresses
2. **Given** a user has both active and inactive keys, **When** they filter by status, **Then** the system shows only keys matching the selected status
3. **Given** a user searches by a key's alias, **When** they type in the search box, **Then** the system filters keys matching the search term in real-time

---

### Edge Cases

- What happens when a user attempts to register a duplicate Pix Key (same email/CPF/phone that already exists on the account)? → System prevents registration and displays "This key is already registered on your account"
- What happens when a user's email address changes? → System requires email revalidation; current email-based key becomes inactive until revalidated, user must register new key with updated email
- What happens when the Pix network is unavailable or unreachable during key registration? → System stores the registration request locally with "pending" status, displays "Registration in progress" to user, and syncs with Pix network when connectivity restored
- What happens if a user loses access to their registered email or phone? → User must deactivate the key before registering it under a different email/phone; this prevents key hijacking
- What happens when a user attempts to register more keys than an account limit [NEEDS CLARIFICATION: maximum number of Pix Keys per user account]? → System prevents registration and displays "You have reached the maximum number of Pix Keys (limit: N). Delete or deactivate unused keys to register new ones."
- What happens if the Pix Key validation service returns an unexpected error? → System displays user-friendly error ("We're having trouble validating your key. Please try again in a few moments.") and allows user to retry without data loss

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to register a new Pix Key by specifying the key type (CPF, Email, Phone) or requesting a random key generation
- **FR-002**: System MUST validate all registered keys against standard Brazilian CPF format, valid email format, and valid phone number format (11-digit mobile or 10-digit landline)
- **FR-003**: System MUST display all registered Pix Keys to the user with metadata including: key type, key value (masked for security), status (active/inactive), creation date, and optional alias
- **FR-004**: System MUST allow users to change a Pix Key status from active to inactive (deactivation) and back to active (reactivation)
- **FR-005**: System MUST prevent duplicate key registration on the same user account (no two keys of the same value can exist)
- **FR-006**: System MUST allow users to permanently delete deactivated Pix Keys; active keys must be deactivated first
- **FR-007**: System MUST allow users to add/edit an alias (nickname) for each Pix Key to help organize and identify keys
- **FR-008**: System MUST support marking one Pix Key as "preferred" for default use in notifications and payment receiving workflows
- **FR-009**: System MUST prevent users from registering more than 5 Pix Keys per account
- **FR-010**: System MUST persist all Pix Key data (registration date, status history, modifications) to enable audit trails and regulatory compliance
- **FR-011**: System MUST provide a search and filter mechanism to find keys by type, status, or alias
- **FR-012**: System MUST validate all keys with the Pix network validation service before marking them as active and ready to receive payments
- **FR-013**: System MUST mask sensitive key information in display (e.g., show "user***@email.com" instead of full email) while showing enough detail for users to identify their keys
- **FR-014**: System MUST handle key registration failures gracefully, display user-friendly error messages, and allow users to retry without data loss
- **FR-015**: System MUST log all key lifecycle events (registration, deactivation, deletion, reactivation) with timestamp and user context for compliance and debugging
- **FR-016**: System MUST ensure only authenticated users can access their own Pix Keys and prevent unauthorized access to other users' key data

### Key Entities

- **User**: Represents a customer/account holder who owns and manages Pix Keys
  - Attributes: user_id, email, phone, created_at, updated_at
  
- **PixKey**: Represents a single Pix Key identifier registered for a user
  - Attributes: key_id, user_id, key_type (CPF/Email/Phone/Random), key_value, status (active/inactive), created_at, updated_at, alias, is_preferred, validation_status, pix_network_id
  
- **PixKeyAudit**: Tracks all changes and events for compliance and debugging
  - Attributes: audit_id, key_id, event_type (registered/activated/deactivated/deleted/revalidated), changed_by (user_id), changed_at, details

- **PixKeyValidation**: Stores validation results from Pix network
  - Attributes: validation_id, key_id, validation_date, is_valid, validation_error, pix_network_response

---

## Success Criteria *(mandatory)*

1. **User Registration Efficiency**: Users can register a Pix Key in under 2 minutes from app launch to confirmation, with clear, guided steps
2. **Key List Accuracy**: User's key list displays all registered keys with 100% accuracy within 3 seconds of page load
3. **Validation Success Rate**: 95% of valid Pix Keys (correct format matching Brazilian standards) pass validation and become active without user retry
4. **Error Recovery**: After an error (e.g., network timeout), users can retry registration and complete it without needing to restart the process from scratch
5. **Data Persistence**: All registered keys and metadata persist across sessions; users see the same key list whether they log in immediately or days later
6. **Deactivation Speed**: Users can deactivate a key and see the status change reflected in under 3 seconds
7. **User Confidence**: 90% of users can complete the core workflow (register → view → deactivate) without requiring help/support
8. **Key Security**: No sensitive key data is exposed in logs, error messages, or API responses; only masked formats shown to users
9. **Compliance Logging**: 100% of key lifecycle events are logged with appropriate timestamps and user context for audit trails
10. **Independent Delivery**: Each P1 user story can be developed, tested, and deployed independently; removing one story does not break others

---

## Assumptions

1. **User Authentication**: Users are already authenticated in the system; this feature assumes a user management/authentication layer already exists and provides `user_id` context
2. **Pix Network Access**: System has access to a Pix network validation API for validating keys conform to Brazilian standards and registering keys for payment receiving capability
3. **Key Limit**: Maximum of 5 Pix Keys per user account is a reasonable business limit aligned with typical user needs and Pix network regulations
4. **Masked Display**: Showing partial key information (e.g., "user***@email.com") is sufficient for users to identify their keys without exposing full sensitive data; system only shows full key during registration confirmation
5. **Status Model**: Keys have two states (active/inactive); they cannot skip deactivation as a safety measure to prevent accidental key loss
6. **Same-User Access**: Users can only manage their own keys; no cross-user management or admin override assumed (admin/delegation features deferred to P2+)
7. **Browser-Based**: Primary interface is a web browser; mobile app/native clients are deferred to P2
8. **Real-Time Validation**: Pix network validation happens synchronously during registration; async validation is deferred if network is slow (queuing for later retry)
9. **No Scheduled Tasks**: Initial MVP focuses on user-triggered actions; scheduled key revalidation, expiration, or cleanup are P2 features
10. **Clean Code Architecture**: Implementation will follow the Python Web Services Constitution with Clean Code Architecture layers (Entities, Use Cases, Controllers, Frameworks)

---

## Compliance & Regulatory Context

- **Pix Regulatory Compliance**: Design complies with Brazilian Central Bank regulations for Pix key management and security
- **Data Privacy**: User key data handling complies with LGPD (Lei Geral de Proteção de Dados) requirements for secure storage and user control
- **Audit Requirements**: All key lifecycle events logged for Central Bank compliance and regulatory audits
- **Security**: No key data stored or transmitted in plaintext; sensitive information masked in UI and logs

---

**Notes:**
- Feature aligns with Python Web Services Constitution's Clean Code Architecture principles
- User scenarios organized by priority to enable incremental MVP development
- Success criteria are technology-agnostic and measurable
- Most design decisions have reasonable defaults; only 2 critical clarifications needed (both marked in User Story 4 and Edge Cases)
