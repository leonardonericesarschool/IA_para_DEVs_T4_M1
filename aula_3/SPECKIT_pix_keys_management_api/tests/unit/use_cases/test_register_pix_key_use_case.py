"""Unit tests for RegisterPixKeyUseCase - Test-Driven Development approach.

These tests are written FIRST to define the expected behavior of the use case.
They specify requirements for:
- Successful registration with various key types
- Duplicate prevention
- Max keys limit enforcement
- Validation error handling
- Audit log integration
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.entities import PixKeyType, PixKeyStatus, PixKeyValidationStatus
from src.entities.pix_key import PixKey
from src.entities.pix_key_audit import PixKeyAudit
from src.exceptions import (
    ValidationError,
    DuplicateKeyError,
    MaxKeysExceededError,
)
from src.repositories import PixKeyRepository, PixKeyAuditRepository
from src.use_cases import RegisterPixKeyUseCase


@pytest.fixture
def mock_pix_key_repository():
    """Create a mock PixKeyRepository for testing."""
    repo = AsyncMock(spec=PixKeyRepository)
    repo.get_by_hash = AsyncMock(return_value=None)  # No duplicates by default
    repo.count_for_user = AsyncMock(return_value=0)  # No existing keys by default
    repo.create = AsyncMock()
    repo.create.side_effect = lambda key: key  # Return the key passed in
    return repo


@pytest.fixture
def mock_audit_repository():
    """Create a mock PixKeyAuditRepository for testing."""
    repo = AsyncMock(spec=PixKeyAuditRepository)
    repo.create_audit_log = AsyncMock()
    return repo


@pytest.fixture
def use_case(mock_pix_key_repository, mock_audit_repository):
    """Create a RegisterPixKeyUseCase with mocked dependencies."""
    return RegisterPixKeyUseCase(
        pix_key_repository=mock_pix_key_repository,
        pix_key_audit_repository=mock_audit_repository,
    )


class TestRegisterPixKeyCPF:
    """Tests for registering Pix keys with CPF type."""

    @pytest.mark.asyncio
    async def test_successful_registration_with_valid_cpf(
        self, use_case, mock_pix_key_repository, mock_audit_repository
    ):
        """Test successful registration with a valid CPF."""
        user_id = str(uuid4())
        cpf = "12345678910"
        alias = "My CPF"

        key, plaintext = await use_case.execute(
            user_id=user_id,
            key_type=PixKeyType.CPF,
            key_value=cpf,
            alias=alias,
        )

        assert key is not None
        assert key.user_id == user_id
        assert key.key_type == PixKeyType.CPF
        assert key.alias == alias
        assert key.status == PixKeyStatus.ACTIVE
        assert key.validation_status == PixKeyValidationStatus.VALID
        assert plaintext == cpf  # Should return plaintext one-time

        # Verify repository was called
        mock_pix_key_repository.create.assert_called_once()
        mock_pix_key_repository.get_by_hash.assert_called_once()
        mock_audit_repository.create_audit_log.assert_called_once()

    @pytest.mark.asyncio
    async def test_registration_fails_with_invalid_cpf_format(
        self, use_case, mock_pix_key_repository
    ):
        """Test registration fails with invalid CPF format."""
        user_id = str(uuid4())
        invalid_cpf = "123"  # Too short

        with pytest.raises(ValidationError) as exc_info:
            await use_case.execute(
                user_id=user_id,
                key_type=PixKeyType.CPF,
                key_value=invalid_cpf,
            )

        assert "CPF" in str(exc_info.value)
        mock_pix_key_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_duplicate_cpf_detection(
        self, use_case, mock_pix_key_repository
    ):
        """Test that duplicate CPF keys are detected and rejected."""
        user_id = str(uuid4())
        cpf = "12345678910"

        # Mock repository to return an existing key (duplicate)
        existing_key = PixKey(
            key_id=str(uuid4()),
            user_id=user_id,
            key_type=PixKeyType.CPF,
            key_value_hash="hash",
            key_value_masked="***.***.***-10",
            status=PixKeyStatus.ACTIVE,
            validation_status=PixKeyValidationStatus.VALID,
        )
        mock_pix_key_repository.get_by_hash.return_value = existing_key

        with pytest.raises(DuplicateKeyError) as exc_info:
            await use_case.execute(
                user_id=user_id,
                key_type=PixKeyType.CPF,
                key_value=cpf,
            )

        assert "already exists" in str(exc_info.value).lower()


class TestRegisterPixKeyEmail:
    """Tests for registering Pix keys with EMAIL type."""

    @pytest.mark.asyncio
    async def test_successful_registration_with_valid_email(
        self, use_case, mock_pix_key_repository, mock_audit_repository
    ):
        """Test successful registration with a valid email."""
        user_id = str(uuid4())
        email = "user@example.com"
        alias = "My Email"

        key, plaintext = await use_case.execute(
            user_id=user_id,
            key_type=PixKeyType.EMAIL,
            key_value=email,
            alias=alias,
        )

        assert key is not None
        assert key.user_id == user_id
        assert key.key_type == PixKeyType.EMAIL
        assert key.alias == alias
        assert plaintext == email

    @pytest.mark.asyncio
    async def test_registration_fails_with_invalid_email_format(
        self, use_case, mock_pix_key_repository
    ):
        """Test registration fails with invalid email format."""
        user_id = str(uuid4())
        invalid_email = "not-an-email"

        with pytest.raises(ValidationError) as exc_info:
            await use_case.execute(
                user_id=user_id,
                key_type=PixKeyType.EMAIL,
                key_value=invalid_email,
            )

        assert "email" in str(exc_info.value).lower()
        mock_pix_key_repository.create.assert_not_called()


class TestRegisterPixKeyPhone:
    """Tests for registering Pix keys with PHONE type."""

    @pytest.mark.asyncio
    async def test_successful_registration_with_valid_phone(
        self, use_case, mock_pix_key_repository, mock_audit_repository
    ):
        """Test successful registration with a valid phone number."""
        user_id = str(uuid4())
        phone = "11987654321"
        alias = "My Phone"

        key, plaintext = await use_case.execute(
            user_id=user_id,
            key_type=PixKeyType.PHONE,
            key_value=phone,
            alias=alias,
        )

        assert key is not None
        assert key.user_id == user_id
        assert key.key_type == PixKeyType.PHONE
        assert key.alias == alias
        assert plaintext == phone

    @pytest.mark.asyncio
    async def test_registration_fails_with_invalid_phone_format(
        self, use_case, mock_pix_key_repository
    ):
        """Test registration fails with invalid phone format."""
        user_id = str(uuid4())
        invalid_phone = "123"  # Too short

        with pytest.raises(ValidationError) as exc_info:
            await use_case.execute(
                user_id=user_id,
                key_type=PixKeyType.PHONE,
                key_value=invalid_phone,
            )

        assert "phone" in str(exc_info.value).lower()


class TestRegisterPixKeyRandom:
    """Tests for registering Pix keys with RANDOM type (generated)."""

    @pytest.mark.asyncio
    async def test_successful_registration_with_random_key_generation(
        self, use_case, mock_pix_key_repository, mock_audit_repository
    ):
        """Test successful registration when key is generated (RANDOM type)."""
        user_id = str(uuid4())

        # No key_value provided for RANDOM type - should be generated
        key, plaintext = await use_case.execute(
            user_id=user_id,
            key_type=PixKeyType.RANDOM,
            key_value=None,
            alias="Generated Key",
        )

        assert key is not None
        assert key.user_id == user_id
        assert key.key_type == PixKeyType.RANDOM
        assert plaintext is not None
        assert len(plaintext) > 0  # Generated key should have content

    @pytest.mark.asyncio
    async def test_random_key_generation_ignores_provided_value(
        self, use_case, mock_pix_key_repository, mock_audit_repository
    ):
        """Test that for RANDOM type, provided key_value is ignored and new one is generated."""
        user_id = str(uuid4())

        key, plaintext = await use_case.execute(
            user_id=user_id,
            key_type=PixKeyType.RANDOM,
            key_value="this-should-be-ignored",
            alias="Generated Key",
        )

        assert key is not None
        assert plaintext != "this-should-be-ignored"  # Should be different


class TestMaxKeysLimit:
    """Tests for the maximum 5 keys per user limit."""

    @pytest.mark.asyncio
    async def test_registration_succeeds_at_fifth_key(
        self, use_case, mock_pix_key_repository, mock_audit_repository
    ):
        """Test that registration succeeds when user has exactly 4 keys (adding 5th)."""
        user_id = str(uuid4())
        mock_pix_key_repository.count_for_user.return_value = 4

        key, plaintext = await use_case.execute(
            user_id=user_id,
            key_type=PixKeyType.CPF,
            key_value="12345678910",
        )

        assert key is not None
        mock_pix_key_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_registration_fails_when_max_keys_exceeded(
        self, use_case, mock_pix_key_repository
    ):
        """Test that registration fails when user already has 5 keys."""
        user_id = str(uuid4())
        mock_pix_key_repository.count_for_user.return_value = 5

        with pytest.raises(MaxKeysExceededError) as exc_info:
            await use_case.execute(
                user_id=user_id,
                key_type=PixKeyType.CPF,
                key_value="12345678910",
            )

        assert "5" in str(exc_info.value)  # Should mention 5-key limit
        mock_pix_key_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_registration_fails_at_sixth_key_attempt(
        self, use_case, mock_pix_key_repository
    ):
        """Test that 6th key is correctly rejected."""
        user_id = str(uuid4())
        mock_pix_key_repository.count_for_user.return_value = 5

        with pytest.raises(MaxKeysExceededError):
            await use_case.execute(
                user_id=user_id,
                key_type=PixKeyType.EMAIL,
                key_value="user@example.com",
            )


class TestAuditLogCreation:
    """Tests for audit log entry creation during registration."""

    @pytest.mark.asyncio
    async def test_audit_log_created_on_successful_registration(
        self, use_case, mock_pix_key_repository, mock_audit_repository
    ):
        """Test that an audit log entry is created after successful registration."""
        user_id = str(uuid4())
        key, plaintext = await use_case.execute(
            user_id=user_id,
            key_type=PixKeyType.CPF,
            key_value="12345678910",
        )

        # Verify audit log was created
        mock_audit_repository.create_audit_log.assert_called_once()
        call_args = mock_audit_repository.create_audit_log.call_args

        # Extract the audit_data dict passed to create_audit_log
        assert call_args is not None
        audit_data = call_args.kwargs
        assert audit_data["user_id"] == user_id
        assert audit_data["operation"] == "REGISTERED"

    @pytest.mark.asyncio
    async def test_audit_log_not_created_on_failed_registration(
        self, use_case, mock_pix_key_repository, mock_audit_repository
    ):
        """Test that audit log is NOT created if registration fails."""
        user_id = str(uuid4())
        mock_pix_key_repository.count_for_user.return_value = 5

        with pytest.raises(MaxKeysExceededError):
            await use_case.execute(
                user_id=user_id,
                key_type=PixKeyType.CPF,
                key_value="12345678910",
            )

        # Audit log should not be created for failed attempts
        mock_audit_repository.create_audit_log.assert_not_called()


class TestKeyMasking:
    """Tests for key masking in responses."""

    @pytest.mark.asyncio
    async def test_response_contains_masked_key_not_plaintext(
        self, use_case, mock_pix_key_repository, mock_audit_repository
    ):
        """Test that the PixKey entity contains masked value, while tuple returns plaintext."""
        user_id = str(uuid4())
        cpf = "12345678910"

        key, plaintext = await use_case.execute(
            user_id=user_id,
            key_type=PixKeyType.CPF,
            key_value=cpf,
        )

        # Entity should have masked value
        assert key.key_value_masked is not None
        assert cpf not in key.key_value_masked  # Plaintext should NOT be in masked

        # Tuple should return plaintext (one-time display)
        assert plaintext == cpf

    @pytest.mark.asyncio
    async def test_cpf_masking_format(
        self, use_case, mock_pix_key_repository, mock_audit_repository
    ):
        """Test that CPF is masked correctly."""
        user_id = str(uuid4())
        cpf = "12345678910"

        key, plaintext = await use_case.execute(
            user_id=user_id,
            key_type=PixKeyType.CPF,
            key_value=cpf,
        )

        # CPF should be masked as ***.***.***.10
        assert key.key_value_masked
        assert "10" in key.key_value_masked  # Last 2 digits visible
        assert key.key_value_masked.count("*") > 0  # Has asterisks

    @pytest.mark.asyncio
    async def test_email_masking_format(
        self, use_case, mock_pix_key_repository, mock_audit_repository
    ):
        """Test that email is masked correctly."""
        user_id = str(uuid4())
        email = "user@example.com"

        key, plaintext = await use_case.execute(
            user_id=user_id,
            key_type=PixKeyType.EMAIL,
            key_value=email,
        )

        # Email domain should be visible, user should be masked
        assert key.key_value_masked
        assert "example.com" in key.key_value_masked
        assert "user" not in key.key_value_masked


class TestValidationErrorHandling:
    """Tests for proper error handling from validation utilities."""

    @pytest.mark.asyncio
    async def test_validation_error_includes_field_name(
        self, use_case, mock_pix_key_repository
    ):
        """Test that validation errors include the field name."""
        user_id = str(uuid4())

        with pytest.raises(ValidationError) as exc_info:
            await use_case.execute(
                user_id=user_id,
                key_type=PixKeyType.CPF,
                key_value="invalid",
            )

        error = exc_info.value
        assert "CPF" in str(error)

    @pytest.mark.asyncio
    async def test_multiple_validation_errors_handled(
        self, use_case, mock_pix_key_repository
    ):
        """Test handling of validation errors from multiple checks."""
        user_id = str(uuid4())

        # First test: invalid email
        with pytest.raises(ValidationError):
            await use_case.execute(
                user_id=user_id,
                key_type=PixKeyType.EMAIL,
                key_value="not-email",
            )

        # Second test: invalid phone
        with pytest.raises(ValidationError):
            await use_case.execute(
                user_id=user_id,
                key_type=PixKeyType.PHONE,
                key_value="123",
            )


class TestAliasBehavior:
    """Tests for alias handling during registration."""

    @pytest.mark.asyncio
    async def test_registration_with_alias(
        self, use_case, mock_pix_key_repository, mock_audit_repository
    ):
        """Test that alias is properly stored with the key."""
        user_id = str(uuid4())
        alias = "My CPF Key"

        key, plaintext = await use_case.execute(
            user_id=user_id,
            key_type=PixKeyType.CPF,
            key_value="12345678910",
            alias=alias,
        )

        assert key.alias == alias

    @pytest.mark.asyncio
    async def test_registration_without_alias(
        self, use_case, mock_pix_key_repository, mock_audit_repository
    ):
        """Test that registration works without providing an alias."""
        user_id = str(uuid4())

        key, plaintext = await use_case.execute(
            user_id=user_id,
            key_type=PixKeyType.CPF,
            key_value="12345678910",
        )

        assert key is not None
        # Alias may be None or default value
